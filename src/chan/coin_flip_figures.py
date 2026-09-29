"""Five figures for the coin-flip gamble, drawn for the blog post about it.

``blog/coin-toss-expected-value-vs-growth.md`` makes its argument in numbers,
and the owner asked on 2026-09-29 for pictures that show it. Each figure below
draws one lesson from quantities :mod:`chan.coin_flip_growth` already computes,
so a figure can only be wrong by drawing the wrong thing, which
``tests/test_coin_flip_figures.py`` checks.

1. :func:`make_stake_figure` draws the exact growth rate against the stake.
   Growth is zero at a stake of 1/11, highest at 1/22, and Chan's 1/10 sits
   just below zero, which is Lesson 4.
2. :func:`make_paths_figure` draws a fan of seeded capital paths over 1,000
   rounds, with the ensemble mean climbing and the median path sinking, which
   is Lessons 1 and 2.
3. :func:`make_distribution_figure` draws the probability of every balance
   1,000 rounds can reach. The median, the starting capital and the ensemble
   mean are marked, and so is the balance the continuous approximation
   compounds to, which falls between two bars. That is Lessons 1 and 5.
4. :func:`make_sign_figure` draws the simulated time average from each of 200
   seeds at two run sizes. The small run straddles zero and the large one
   does not, which is the first problem in Lesson 6.
5. :func:`make_estimator_figure` draws two estimates of the ensemble growth
   from each of 20 seeds. Averaging final wealth reads low on every one, and
   averaging each toss's return lands on the true value, which is the second
   problem in Lesson 6.

This reopens a row of the considered-and-rejected register in
``docs/design.md``, which cut a figure for the coin-flip divergence on the
cost of keeping copies in step. The owner chose the first three figures
knowing that, and the row now records the reversal. The last two followed
on the same day, to make Lesson 6 easier to follow.

None of the figures reads a vintage, because the gamble is arithmetic on a
known coin rather than market data.
Regenerate after any change that moves what they draw::

    uv run python -m chan.coin_flip_figures
"""

from __future__ import annotations

import functools
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, PercentFormatter

from chan.coin_flip_growth import (
    BOOK_SEED,
    LOSS,
    START_CAPITAL,
    WIN,
    _flip_log_returns,
    capital_horizon,
    gamble_moments,
    log_return_sd,
    simulate,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, GROUND, INK, LOST, MUTED, RULE, SURFACE

STAKE_FIGURE = "coin_flip_growth_by_stake.png"
PATHS_FIGURE = "coin_flip_capital_paths.png"
DISTRIBUTION_FIGURE = "coin_flip_final_balances.png"
SIGN_FIGURE = "coin_flip_sign_by_run_size.png"
ESTIMATOR_FIGURE = "coin_flip_ensemble_estimators.png"

#: Rounds every capital figure runs, matching the horizon the post quotes.
ROUNDS = 1000

#: Paths in the fan. Enough to show the spread, few enough that each line is
#: still a line rather than a solid band.
FAN_PATHS = 200

#: The widest stake the growth curve draws. At 0.11 the exact rate is about
#: −0.0012, close to the mirror of the +0.0011 peak, so the curve's two sides
#: get equal room and the peak is not flattened by a deep tail.
MAX_STAKE = 0.11

#: Head counts the balance distribution draws. Outside this range the
#: probabilities sum to about 1.3e-4, so nothing visible is cut.
HEADS_SHOWN = (440, 560)

#: The two run sizes the sign figure compares, as (rounds, traders). They are
#: the sizes ``tests/test_coin_flip_growth.py`` pins: the small one gets the
#: sign wrong on 56 of the first 200 seeds and the large one on none.
RUN_SIZES = ((100, 200), (1000, 1000))

#: Seeds each sign histogram counts, the same sweep the growth tests use.
SIGN_SEEDS = 200

#: Bin width for the sign histograms, in growth per round. Zero is a bin edge,
#: so no bar mixes estimates on both sides of it.
SIGN_BIN = 1e-4

#: The estimator figure's run, as (rounds, traders, seeds). The same size and
#: seed count the growth tests use to show the wealth average reading low.
ESTIMATOR_RUN = (5000, 1000, 20)


@dataclass(frozen=True)
class StakeCurve:
    stakes: np.ndarray
    growth: np.ndarray


@dataclass(frozen=True)
class Balances:
    """Every balance 1,000 rounds can reach, with the chance of reaching it."""

    heads: np.ndarray
    balance: np.ndarray
    probability: np.ndarray
    median: float
    mean: float
    approximated: float
    share_below_start: float
    share_at_or_above_mean: float


def _plain_text(make):
    """Draw with matplotlib's math parsing off, so a dollar sign is a dollar sign.

    Every label here prints dollars, and two dollar signs in one string turn
    the text between them into an italic formula. The inset title did exactly
    that on its first draw.
    """

    @functools.wraps(make)
    def draw(*args, **kwargs):
        with matplotlib.rc_context({"text.parse_math": False}):
            return make(*args, **kwargs)

    return draw


def _dollars(x: float, _pos: object = None) -> str:
    """A tick label in whole dollars, or cents below one dollar."""
    if x >= 1:
        return f"${x:,.0f}"
    return f"${x:.2f}" if x >= 0.01 else f"${x:.0e}"


def _signed_rate(y: float, _pos: object = None) -> str:
    """A growth-rate tick with a typographic minus, and a bare zero."""
    return "0" if abs(y) < 1e-12 else f"{y:+.4f}".replace("-", "−")


def _style(ax) -> None:
    ax.set_facecolor(GROUND)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(RULE)
    ax.tick_params(colors=MUTED, labelsize=9.5)
    ax.grid(axis="y", color=RULE, lw=0.6, alpha=0.7)
    ax.set_axisbelow(True)


def _title(fig: Figure, title: str, note: str) -> None:
    fig.suptitle(title, x=0.01, ha="left", color=INK, fontsize=13.5, fontweight="bold")
    fig.text(0.01, 0.012, note, color=MUTED, fontsize=10, linespacing=1.45)


def stake_curve(points: int = 441) -> StakeCurve:
    """The exact growth rate at each stake from 0 to :data:`MAX_STAKE`.

    A stake ``f`` is expressed to :func:`gamble_moments` as a capital of
    ``LOSS / f``, which keeps the payoff odds and moves only the fraction at
    risk. Zero stake is growth of zero and is set directly.
    """
    stakes = np.linspace(0.0, MAX_STAKE, points)
    growth = np.array(
        [0.0 if f == 0 else gamble_moments(capital=LOSS / f).growth_exact for f in stakes]
    )
    return StakeCurve(stakes=stakes, growth=growth)


def final_balances() -> Balances:
    """The 1,001 balances after :data:`ROUNDS` rounds and their probabilities.

    The balance depends only on the head count ``h``, so each is the starting
    capital times ``1.11**h * 0.90**(ROUNDS - h)``, reached with binomial
    probability ``comb(ROUNDS, h) / 2**ROUNDS``.
    """
    up, down = 1 + WIN / START_CAPITAL, 1 - LOSS / START_CAPITAL
    heads = np.arange(ROUNDS + 1)
    balance = np.array([START_CAPITAL * up**h * down ** (ROUNDS - h) for h in heads])
    probability = np.array([math.comb(ROUNDS, int(h)) / 2**ROUNDS for h in heads])
    moments = gamble_moments()
    horizon = capital_horizon(ROUNDS, moments)
    return Balances(
        heads=heads,
        balance=balance,
        probability=probability,
        median=horizon.time_average_capital,
        mean=horizon.ensemble_capital,
        approximated=START_CAPITAL * math.exp(moments.growth_continuous * ROUNDS),
        share_below_start=float(probability[balance < START_CAPITAL].sum()),
        share_at_or_above_mean=float(probability[balance >= horizon.ensemble_capital].sum()),
    )


def _save(fig: Figure, out: Path | None, name: str) -> Figure:
    path = out if out is not None else FIGURES_DIR / name
    fig.savefig(path, facecolor=SURFACE)
    return fig


@_plain_text
def make_stake_figure(out: Path | None = None) -> Figure:
    """Growth per round against the stake, with three stakes marked."""
    curve = stake_curve()
    chan = gamble_moments()
    best = gamble_moments(capital=LOSS * 22)

    fig = Figure(figsize=(10, 5.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)

    ax.axhline(0, color=MUTED, lw=0.9)
    grows = curve.growth >= 0
    ax.fill_between(curve.stakes, curve.growth, 0, where=grows, color=GOOD, alpha=0.18, lw=0)
    ax.fill_between(curve.stakes, curve.growth, 0, where=~grows, color=LOST, alpha=0.18, lw=0)
    ax.plot(curve.stakes, curve.growth, color=INK, lw=2)

    marks = [
        (
            best.stake_fraction,
            best.growth_exact,
            GOOD,
            "best stake, 1/22\n+0.0011351 per round",
            (-60, 18),
        ),
        (chan.breakeven_stake, 0.0, MUTED, "break-even, 1/11\ngrowth zero", (-120, -40)),
        (
            chan.stake_fraction,
            chan.growth_exact,
            LOST,
            "Chan’s stake, 1/10\n−0.00050025 per round",
            (-150, -42),
        ),
    ]
    for x, y, colour, label, offset in marks:
        ax.plot([x], [y], "o", ms=8, color=colour, mec=SURFACE, mew=2, zorder=3)
        ax.annotate(
            label,
            (x, y),
            xytext=offset,
            textcoords="offset points",
            color=INK,
            fontsize=10,
            arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8},
        )

    ax.set_xlim(0, MAX_STAKE)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.yaxis.set_major_formatter(FuncFormatter(_signed_rate))
    ax.set_xlabel("stake, as a share of capital at risk each round", color=INK, fontsize=10.5)
    ax.set_ylabel("growth per round, exact", color=INK, fontsize=10.5)
    _title(
        fig,
        "Chan’s stake of 1/10 shrinks capital, and a stake of 1/22 grows it fastest",
        "Fair coin, heads pays 1.1 times the stake, tails loses it. "
        "Growth is ½ ln(1 + 1.1f) + ½ ln(1 − f) for a stake f.\n"
        "Shaded green where capital grows, red where it shrinks.",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.96))
    fig.curve = curve
    return _save(fig, out, STAKE_FIGURE)


@_plain_text
def make_paths_figure(out: Path | None = None, seed: int = BOOK_SEED) -> Figure:
    """A fan of seeded capital paths with the ensemble mean and the median path."""
    logs = _flip_log_returns(ROUNDS, FAN_PATHS, seed, WIN, LOSS, START_CAPITAL)
    paths = START_CAPITAL * np.exp(np.cumsum(logs, axis=1))
    paths = np.hstack([np.full((FAN_PATHS, 1), START_CAPITAL), paths])
    rounds = np.arange(ROUNDS + 1)
    sample_mean = float(paths[:, -1].mean())
    moments = gamble_moments()
    mean = START_CAPITAL * np.exp(moments.ensemble_log_growth * rounds)
    median = START_CAPITAL * np.exp(moments.growth_exact * rounds)

    fig = Figure(figsize=(10, 5.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.set_yscale("log")

    for path in paths:
        ax.plot(rounds, path, color=MUTED, lw=0.5, alpha=0.18)
    ax.axhline(START_CAPITAL, color=INK, lw=1, ls=(0, (5, 3)), alpha=0.7, zorder=3)
    ax.plot(rounds, mean, color=ACCENT, lw=2.2)
    ax.plot(rounds, median, color=LOST, lw=2.2)

    ax.annotate(
        f"ensemble mean, all possible traders\n{_dollars(mean[-1])}",
        (ROUNDS, mean[-1]),
        xytext=(-8, 12),
        textcoords="offset points",
        ha="right",
        va="bottom",
        color=INK,
        fontsize=10.5,
        fontweight="bold",
    )
    ax.annotate(
        f"median trader\n{_dollars(median[-1])}",
        (ROUNDS, median[-1]),
        xytext=(-8, -26),
        textcoords="offset points",
        ha="right",
        va="top",
        color=INK,
        fontsize=10.5,
        fontweight="bold",
    )

    ax.set_xlim(0, ROUNDS)
    ax.yaxis.set_major_formatter(FuncFormatter(_dollars))
    ax.set_xlabel("round", color=INK, fontsize=10.5)
    ax.set_ylabel("capital, log scale", color=INK, fontsize=10.5)
    _title(
        fig,
        "The ensemble mean climbs while the median trader loses",
        f"{FAN_PATHS} simulated traders from $1,000, seed {seed}, tosses drawn with numpy’s "
        "rng.integers. Dashed: the starting capital.\n"
        f"The {FAN_PATHS} drawn average {_dollars(sample_mean)} at round {ROUNDS:,}, short of the "
        "gold line, because the lucky paths that carry the mean are too rare to draw.",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.96))
    fig.paths = paths
    fig.sample_mean = sample_mean
    fig.mean = mean
    fig.median = median
    return _save(fig, out, PATHS_FIGURE)


@_plain_text
def make_distribution_figure(out: Path | None = None) -> Figure:
    """The probability of each reachable balance after 1,000 rounds, on a log axis."""
    b = final_balances()
    low, high = HEADS_SHOWN
    shown = (b.heads >= low) & (b.heads <= high)
    x, p = b.balance[shown], b.probability[shown]

    fig = Figure(figsize=(10, 5.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.set_xscale("log")

    # Each bar spans the gap to its neighbours on the log axis, less a small
    # surface gap, so bars read as separate outcomes rather than a histogram.
    step = (1 + WIN / START_CAPITAL) / (1 - LOSS / START_CAPITAL)
    half = math.sqrt(step)
    ax.bar(
        x / half * 1.02,
        p,
        width=x * half / 1.02 - x / half * 1.02,
        align="edge",
        color=[LOST if v < START_CAPITAL else GOOD for v in x],
        alpha=0.8,
        lw=0,
    )

    peak = p.max()
    lines = [
        (b.median, LOST, f"median trader\n{_dollars(b.median)}", "right"),
        (START_CAPITAL, MUTED, "starting capital\n$1,000", "left"),
        (b.mean, ACCENT, f"ensemble mean\n{_dollars(b.mean)}", "left"),
    ]
    for value, colour, label, side in lines:
        ax.axvline(value, color=colour, lw=1.8)
        ax.annotate(
            label,
            (value, peak * 1.04),
            xytext=(-6 if side == "right" else 6, 0),
            textcoords="offset points",
            ha=side,
            va="bottom",
            color=INK,
            fontsize=10,
            fontweight="bold",
        )
    # The approximation sits 1.2% below the median balance on an axis spanning
    # ten orders of magnitude, so on the main axes it lands on a bar and says
    # the opposite of what it means. An inset on a linear axis shows the gap.
    inset = ax.inset_axes((0.035, 0.42, 0.3, 0.5))
    inset.set_facecolor(SURFACE)
    for side in ("top", "right"):
        inset.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        inset.spines[side].set_color(RULE)
    inset.tick_params(colors=MUTED, labelsize=10)
    near = [ROUNDS // 2 - 1, ROUNDS // 2]
    for h in near:
        colour = LOST if b.balance[h] < START_CAPITAL else GOOD
        inset.vlines(b.balance[h], 0, b.probability[h], color=colour, lw=3)
        inset.annotate(
            f"{h} heads\n{_dollars(b.balance[h])}",
            (b.balance[h], b.probability[h]),
            xytext=(4, 4),
            textcoords="offset points",
            ha="left",
            va="bottom",
            color=INK,
            fontsize=10,
        )
    inset.axvline(b.approximated, color=INK, lw=1.2, ls=":")
    inset.annotate(
        f"{_dollars(b.approximated)}, the\napproximation",
        (b.approximated, b.probability[near[1]] * 0.45),
        xytext=(-8, 0),
        textcoords="offset points",
        ha="right",
        va="center",
        color=INK,
        fontsize=10,
    )
    inset.set_xlim(470, 690)
    inset.set_xticks([500, 550, 600, 650])
    inset.set_ylim(0, b.probability[near[1]] * 1.45)
    inset.set_yticks([])
    inset.xaxis.set_major_formatter(FuncFormatter(_dollars))
    inset.set_title(
        f"zoomed near $600: no balance at {_dollars(b.approximated)}",
        color=INK,
        fontsize=10,
        loc="left",
    )
    fig.inset = inset

    ax.set_ylim(0, peak * 1.3)
    ax.xaxis.set_major_formatter(FuncFormatter(_dollars))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=1))
    ax.set_xlabel("balance after 1,000 rounds, log scale", color=INK, fontsize=10.5)
    ax.set_ylabel("share of traders", color=INK, fontsize=10.5)
    _title(
        fig,
        f"{b.share_below_start:.1%} of traders end below $1,000, "
        f"and {b.share_at_or_above_mean:.1%} reach the ensemble mean",
        f"One bar per head count from {low} to {high}, with its binomial probability. "
        "Red bars end below the starting capital.\n"
        "The mean is an average, not a balance any head count gives, and neither is the "
        "approximation’s balance in the inset.",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.96))
    fig.balances = b
    return _save(fig, out, DISTRIBUTION_FIGURE)


@dataclass(frozen=True)
class SignRun:
    """The simulated time average from each seed at one run size."""

    rounds: int
    traders: int
    estimates: np.ndarray
    standard_error: float

    @property
    def wrong_sign(self) -> int:
        return int((self.estimates > 0).sum())


def sign_runs() -> tuple[SignRun, ...]:
    """One :class:`SignRun` per entry of :data:`RUN_SIZES`."""
    runs = []
    for rounds, traders in RUN_SIZES:
        estimates = np.array(
            [simulate(rounds, traders, seed).time_average_growth for seed in range(SIGN_SEEDS)]
        )
        runs.append(
            SignRun(
                rounds=rounds,
                traders=traders,
                estimates=estimates,
                standard_error=log_return_sd() / math.sqrt(rounds * traders),
            )
        )
    return tuple(runs)


@_plain_text
def make_sign_figure(out: Path | None = None) -> Figure:
    """Histograms of the simulated time average at two run sizes, on one axis."""
    runs = sign_runs()
    truth = gamble_moments().growth_exact
    low = min(r.estimates.min() for r in runs)
    high = max(r.estimates.max() for r in runs)
    edges = np.arange(
        math.floor(low / SIGN_BIN) * SIGN_BIN,
        math.ceil(high / SIGN_BIN) * SIGN_BIN + SIGN_BIN / 2,
        SIGN_BIN,
    )

    fig = Figure(figsize=(10, 6.4), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    axes = fig.subplots(len(runs), 1, sharex=True)
    for ax, run in zip(axes, runs, strict=True):
        _style(ax)
        counts, _ = np.histogram(run.estimates, bins=edges)
        centres = (edges[:-1] + edges[1:]) / 2
        ax.bar(
            centres,
            counts,
            width=SIGN_BIN * 0.9,
            color=[LOST if c > 0 else MUTED for c in centres],
            lw=0,
        )
        ax.axvline(0, color=INK, lw=1.2)
        ax.axvline(truth, color=ACCENT, lw=1.8, ls=(0, (5, 3)))
        ax.set_ylim(0, counts.max() * 1.25)
        ax.set_ylabel("seeds", color=INK, fontsize=10.5)
        ax.set_title(
            f"{run.rounds:,} rounds × {run.traders:,} traders: "
            f"{run.wrong_sign} of {SIGN_SEEDS} seeds get the sign wrong",
            color=INK,
            fontsize=11.5,
            loc="left",
            fontweight="bold",
        )
    axes[0].annotate(
        f"true growth, {_signed_rate(truth)}",
        (truth, axes[0].get_ylim()[1] * 0.92),
        xytext=(-6, 0),
        textcoords="offset points",
        ha="right",
        color=INK,
        fontsize=10,
    )
    axes[0].annotate(
        "zero",
        (0, axes[0].get_ylim()[1] * 0.92),
        xytext=(6, 0),
        textcoords="offset points",
        ha="left",
        color=INK,
        fontsize=10,
    )
    axes[-1].xaxis.set_major_formatter(FuncFormatter(_signed_rate))
    axes[-1].set_xlabel("simulated time-average growth per round", color=INK, fontsize=10.5)
    small, large = runs
    _title(
        fig,
        "A small simulation gets the sign wrong more than a quarter of the time",
        f"Each bar counts seeds whose estimate falls in a {SIGN_BIN:.4f}-wide range. Red bars sit "
        "right of zero, where the losing bet looks like a winner.\n"
        f"Standard error {small.standard_error:.2e} for the small run and "
        f"{large.standard_error:.2e} for the large one, against a true growth of "
        f"{_signed_rate(truth)}.",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.96))
    fig.runs = runs
    fig.edges = edges
    return _save(fig, out, SIGN_FIGURE)


@dataclass(frozen=True)
class Estimates:
    """Two estimates of the ensemble growth per round from each seed."""

    wealth_average: np.ndarray
    per_toss: np.ndarray
    truth: float


def ensemble_estimates() -> Estimates:
    """Both estimators from the same draws, at :data:`ESTIMATOR_RUN`.

    The wealth average is the log of the mean final wealth divided by the
    rounds, which ``chan.coin_flip_growth.simulate`` rejects. The per-toss
    estimate is the one it uses: the mean simple return of every toss,
    converted to a log rate.
    """
    rounds, traders, seeds = ESTIMATOR_RUN
    wealth, toss = [], []
    for seed in range(seeds):
        logs = _flip_log_returns(rounds, traders, seed, WIN, LOSS, START_CAPITAL)
        wealth.append(math.log(np.exp(logs.sum(axis=1)).mean()) / rounds)
        toss.append(math.log1p(float(np.expm1(logs).mean())))
    return Estimates(
        wealth_average=np.array(wealth),
        per_toss=np.array(toss),
        truth=gamble_moments().ensemble_log_growth,
    )


@_plain_text
def make_estimator_figure(out: Path | None = None) -> Figure:
    """A dot strip of the two ensemble estimators against the true value."""
    e = ensemble_estimates()
    rounds, traders, seeds = ESTIMATOR_RUN

    fig = Figure(figsize=(10, 4.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)

    rows = [
        (1, e.wealth_average, LOST, "log of the mean\nfinal wealth"),
        (0, e.per_toss, MUTED, "mean of each\ntoss’s return"),
    ]
    for y, values, colour, _ in rows:
        # The per-toss dots overlap almost exactly, and a white edge on each
        # draws a halo that reads as a bracket, so that row has none.
        ax.plot(
            values,
            np.full(len(values), y, dtype=float),
            "o",
            ms=9,
            color=colour,
            mec=SURFACE if y == 1 else "none",
            mew=1.5,
            alpha=0.85,
        )
    ax.axvline(e.truth, color=ACCENT, lw=2)
    ax.annotate(
        f"true ensemble growth\nln(1.005) = {e.truth:.7f}",
        (e.truth, 1.45),
        xytext=(-8, 0),
        textcoords="offset points",
        ha="right",
        va="center",
        color=INK,
        fontsize=10,
    )
    ax.annotate(
        f"all {seeds} dots, within 0.0001 of the true value",
        (e.per_toss.min(), 0),
        xytext=(-14, 0),
        textcoords="offset points",
        ha="right",
        va="center",
        color=INK,
        fontsize=10,
    )
    ax.set_yticks([y for y, *_ in rows], [label for *_, label in rows])
    ax.tick_params(axis="y", labelsize=10.5, colors=INK)
    ax.set_ylim(-0.6, 1.8)
    ax.set_xlim(0.002, 0.0055)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.4f}"))
    ax.set_xlabel("estimated ensemble growth per round", color=INK, fontsize=10.5)
    _title(
        fig,
        f"Averaging final wealth reads low on all {seeds} seeds",
        f"{traders:,} simulated traders playing {rounds:,} rounds, one dot per seed. "
        "The wealth average misses the rare lucky paths that carry the mean.\n"
        "Averaging each toss’s return needs no rare paths and lands within 0.0001 of "
        "the true value every time.",
    )
    fig.tight_layout(rect=(0, 0.09, 1, 0.95))
    fig.estimates = e
    return _save(fig, out, ESTIMATOR_FIGURE)


def main() -> None:
    for make, name in (
        (make_stake_figure, STAKE_FIGURE),
        (make_paths_figure, PATHS_FIGURE),
        (make_distribution_figure, DISTRIBUTION_FIGURE),
        (make_sign_figure, SIGN_FIGURE),
        (make_estimator_figure, ESTIMATOR_FIGURE),
    ):
        make()
        print(f"wrote {FIGURES_DIR / name}")


if __name__ == "__main__":
    main()
