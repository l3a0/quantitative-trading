"""Chan's PCA factor model, Example 7.4, on the S&P 600 file every printout loads.

Every other factor model in the book names its factors in advance. This one
takes them from the return matrix itself with principal component analysis,
assumes the factor returns carry momentum, buys the 50 stocks with the highest
expected return and shorts the 50 with the lowest. At Kindle location 4051
Chan reports "only 2% (MATLAB) to 4% (Python and R)" a year with no costs, and
says the difference among the programs is "essentially round off errors".

That sentence is what this module tests. Each printout is transcribed as its
own function, because the programs differ in far more than round-off, and the
report sets the four against each other.

Four sources, all of them Chan's, and all four load ``IJR_20080114``.

1. **The first edition's MATLAB**, ``example7_4.m`` in the mirror
   [egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading)
   at ``1a71950``, which ``data/README.md`` already names. It prints
   ``avgret`` as −1.8099.
2. **The revised edition's MATLAB**, printed on pp. 163 and 164 and reposted at
   pinhaocheng/epchan-quant_trading_MATLAB_codes ``7430b84``. It prints
   ``AvgAnnRet=0.020205 Sharpe=0.211120``.
3. **The revised edition's Python**, printed on pp. 164 and 165 and reposted at
   pinhaocheng/epchan-quant_trading_Python_codes ``5fcab61``. It prints three
   figures to 17 digits.
4. **The revised edition's R**, printed on pp. 165 to 167. It prints the
   Python's three figures, digit for digit. It sources ``calculateReturns.R``,
   which the book does not print and no public copy carries, and this repo has
   no R runtime, so :func:`revised_r_reading` is a reading of the printed code
   rather than a run of it.

The page numbers are the Kindle Cloud Reader's footer, read on 2026-10-03.

**What each program computes.** All four take a lookback of 252, five
factors and 50 stocks a side, and charge no cost.

- :func:`first_edition_matlab` takes the 252 returns ending today, demeans each
  stock, keeps the five eigenvectors of the covariance with the largest
  eigenvalues, fits today's demeaned return on them with ``ols``, and adds the
  mean back. Its daily figure is ``smartsum`` over 100 positions of ±1 with no
  division by capital, so −1.8099 is a sum over positions rather than a return
  on capital. Its mean runs over 1,005 rows, 252 of them zeros from before the
  first trade.
- :func:`revised_matlab` takes the 252 returns ending yesterday and runs
  ``pca`` with stocks as observations and days as variables. It regresses
  today's cross-section of returns on an intercept and the first five scores
  with ``mvregress``, ranks on the fitted values, divides each day by gross
  capital, and takes its mean over the days that trade. Its ``smartstd`` is
  book two's. The printed 0.211120 lands with it and not with the first
  edition's, and the repost at ``7430b84`` carries book two's file.
- :func:`revised_python` takes the 251 returns ending yesterday, runs PCA with
  days as observations, regresses each stock's returns on an intercept and the
  five factor series, and ranks on the summed fitted values.
- :func:`revised_r_reading` takes the 251 returns ending today. Its PCA is not
  the Python's: ``prcomp(t(R))`` treats stocks as observations, and
  ``t(PCA$x[1:numFactors,])`` takes the scores of the first five stocks,
  indexed by component, as its regressors. Each stock's returns are regressed
  on an intercept and those, and it ranks on the summed fitted values.

**The Python's PCA changes no position, and neither does the R's.** A
regression with an intercept leaves residuals that sum to zero, so a stock's
summed fitted value is its summed return over the window, whatever the other
regressors are. Both programs therefore rank on plain momentum.
:func:`summed_returns` is that ranking, and ``tests/test_pca_factor.py`` holds
the Python's positions equal to it on every day.

**Three of the Python's bookkeeping choices move its figures.** Each is
transcribed rather than fixed, and each lowers the figure toward the MATLAB's.
The report prints what each gives when it is changed.

1. ``idxSort[np.arange(-topN, -1)]`` buys 49 stocks, the ones ranked second to
   50th, so the top-ranked stock is never bought.
2. ``positionsTable[capital==0,]=0`` zeroes every row whose previous row
   holds nothing, and the first day's book is one of those rows, so the
   strategy never earns on it.
3. ``np.nanmean`` runs over all 1,006 rows, including the ones that hold no
   position, and ``np.nanstd`` divides by n.

The R buys 52, from ``(length(result$ix)-topN-1):length(result$ix)``.

**What changed on the way over.** Six things, and none moves a position.

1. The closes are read as committed vintages through
   :func:`chan.series.load_panel` rather than loaded from the ``.mat`` or the
   text file. ``data/README.md`` records that the two agree.
2. MATLAB's ``eig`` is :func:`numpy.linalg.eigh`, which returns the
   eigenvalues of a symmetric matrix in the same ascending order. An SVD of
   the demeaned returns gives the same positions in half the time, and was not
   used, so the transcription reads line for line against the script.
3. MATLAB's ``pca`` and ``sklearn``'s ``PCA`` are an SVD of the centred
   matrix, and ``ols``, ``mvregress`` and ``LinearRegression`` are least
   squares, which :func:`numpy.linalg.lstsq` gives. This module does not use
   ``scikit-learn``, which the repo carries only for :mod:`chan.cpo`'s model.
4. The first edition's ``smartcov`` demeans each stock a second time, on rows
   already demeaned, and divides by n. Neither moves an eigenvector.
5. The revised MATLAB's ``onewaytcost`` is 0, so its cost term is not carried.
6. pandas 3's ``ffill()`` and ``pct_change(fill_method=None)`` stand in for
   the Python's ``fillna(method='ffill')`` and default ``pct_change()``, which
   pandas 3 removed or changed. The frame is already filled when the returns
   are taken.

**One splice in the file.** PMC holds two price histories under one symbol. It
closes at 6.02 on 2004-03-12, is missing for 851 days, and resumes at 17.25 on
2007-08-01. The three printouts that run forward-fill, as does the R reading
with ``fill=True``, so that gap is one day's return. :func:`without` reruns a
program without it, and the report prints the result beside the verdicts.
The scale-break guard is not applied, for the reason the comment above
``FLAGGED_IN_CHANS_MAT_FILES`` in ``tests/test_scale_breaks.py`` gives.

**Every figure here is about survivors.** ``IJR_20080114.mat`` holds the 600
companies in the index on 2008-01-14, carried backwards.
[Issue 269](https://github.com/l3a0/quantitative-trading/issues/269) is where
the strategy is run on the index as it stood each day.

Every result here is exploratory. Reproducing Chan's figures spends the 2004
to 2008 sample on a rule he chose, so the run says whether his numbers
reproduce on his file and nothing about whether a statistical factor model
earns money. ``tests/test_pca_factor.py`` is the single authority for every
number any prose surface quotes about Example 7.4.

Usage:
    python -m chan.pca_factor
"""

from __future__ import annotations

import argparse
import math
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.matlab_helpers import (
    backshift,
    matlab_sort,
    smartmean,
    smartstd_book_two,
    smartstd_first_edition,
    smartsum,
)
from chan.series import load_panel, panel_line
from chan.vintage import VintageEntry, VintageUnavailable

SMALL_CAPS = "IJR_20080114.mat"

#: ``lookback``, ``numFactors`` and ``topN`` in every printout.
LOOKBACK = 252
FACTORS = 5
TOP_N = 50
#: The annualisation every printout uses.
TRADING_DAYS = 252

#: Which ranks each printout buys, counted from the top of an ascending sort.
#: MATLAB's ``end-topN+1:end`` is the top 50. The Python's
#: ``np.arange(-topN, -1)`` stops before the last index, so it buys the 49
#: ranked second to 50th and never the top-ranked stock. The R's
#: ``(length-topN-1):length`` is the top 52.
MATLAB_LONGS = slice(-TOP_N, None)
PYTHON_LONGS = slice(-TOP_N, -1)
R_LONGS = slice(-(TOP_N + 2), None)

#: Location 4051's two figures, in percent.
BOOK_MATLAB_PERCENT = 2
BOOK_PYTHON_R_PERCENT = 4

#: What each printout's comment lines print, as they print it.
FIRST_EDITION_PRINTS = "-1.8099"
REVISED_MATLAB_PRINTS = ("0.020205", "0.211120")
#: The Python's annual return, annualised standard deviation and Sharpe ratio.
PYTHON_PRINTS = ("0.04052422056844459", "0.07002908500498846", "0.5786769963588398")
#: The R block prints the same three lines.
R_PRINTS = ("0.04052422056844459", "0.07002908500498846", "0.5786769963588398")

#: The tolerance a figure printed to 17 digits is held to.
DIGITS_17 = 1e-12

#: The column holding two price histories under one symbol.
SPLICED = "PMC"


@dataclass(frozen=True)
class Run:
    """What one printout's program gives.

    ``positions`` is the program's ``positionsTable``, one row per day of the
    file, and ``daily`` is its ``ret`` vector over the same rows. ``annual`` is
    the figure every printout prints. ``stdev`` is the annualised standard
    deviation where the program prints one, and ``sharpe`` the Sharpe ratio,
    each NaN where the program prints none.
    """

    name: str
    positions: np.ndarray
    daily: np.ndarray
    annual: float
    stdev: float
    sharpe: float

    @property
    def traded(self) -> np.ndarray:
        """The rows earning a return, which are the rows after a day with a position."""
        return _traded(self.positions)


def _traded(positions: np.ndarray) -> np.ndarray:
    return np.nansum(np.abs(backshift(1, positions)), axis=1) > 0


# --- each day's expected returns ---------------------------------------------


def first_edition_expected(window: np.ndarray) -> np.ndarray:
    """``example7_4.m``'s ``Rexp`` from a stocks-by-days window ending today.

    The mean is taken out of each stock, the five eigenvectors of the
    covariance with the largest eigenvalues are the exposures, and today's
    demeaned return is fitted on them. The mean goes back in afterwards.
    """
    average = window.mean(axis=1, keepdims=True)
    centred = window - average
    covariance = centred @ centred.T / centred.shape[1]
    _, vectors = np.linalg.eigh(covariance)
    exposures = vectors[:, -FACTORS:]
    factor_returns = np.linalg.lstsq(exposures, centred[:, -1], rcond=None)[0]
    return average[:, 0] + exposures @ factor_returns


def revised_matlab_expected(window: np.ndarray, today: np.ndarray) -> np.ndarray:
    """The revised MATLAB's ``Rexp``: today's returns fitted on five PCA scores.

    ``window`` is stocks by days ending yesterday, so each stock is an
    observation. ``pca`` centres each day across the stocks and the scores are
    the stocks' coordinates on the first five components.
    """
    centred = window - window.mean(axis=0, keepdims=True)
    left, singular, _ = np.linalg.svd(centred, full_matrices=False)
    design = np.column_stack([np.ones(len(window)), left[:, :FACTORS] * singular[:FACTORS]])
    return design @ np.linalg.lstsq(design, today, rcond=None)[0]


def python_expected(window: np.ndarray) -> np.ndarray:
    """The Python's ``Rexp``: each stock's fitted returns on five factor series, summed.

    ``window`` is stocks by days, and the PCA runs with days as observations,
    so its scores are five daily factor returns. Each stock's returns are
    regressed on an intercept and those five, and the fitted values are summed
    over the days. With the intercept in the regression that sum is the
    stock's summed return, which :func:`summed_returns` gives directly.
    """
    days = window.T
    centred = days - days.mean(axis=0, keepdims=True)
    left, singular, _ = np.linalg.svd(centred, full_matrices=False)
    design = np.column_stack([np.ones(len(days)), left[:, :FACTORS] * singular[:FACTORS]])
    return (design @ np.linalg.lstsq(design, days, rcond=None)[0]).sum(axis=0)


def summed_returns(window: np.ndarray) -> np.ndarray:
    """Each stock's summed return over the window, the ranking the Python and R reduce to."""
    return window.sum(axis=1)


# --- the programs --------------------------------------------------------------


def _hold(
    positions: np.ndarray, row: int, has: np.ndarray, order: np.ndarray, longs: slice
) -> None:
    positions[row, has[order[:TOP_N]]] = -1.0
    positions[row, has[order[longs]]] = 1.0


def matlab_returns(prices: np.ndarray) -> np.ndarray:
    """``(mycls - backshift(1, mycls)) ./ backshift(1, mycls)``, each day's return."""
    previous = backshift(1, prices)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (prices - previous) / previous


def first_edition_matlab(closes: pd.DataFrame) -> Run:
    """``example7_4.m`` from the first-edition mirror, which prints ``avgret`` as −1.8099."""
    prices = closes.ffill().to_numpy(dtype=float)  # fillMissingData(cl)
    returns = matlab_returns(prices)
    positions = np.zeros_like(prices)
    for t in range(LOOKBACK, len(prices)):  # for t=lookback+1:length(tday)
        window = returns[t - LOOKBACK + 1 : t + 1].T  # dailyret(t-lookback+1:t,:)'
        has = np.flatnonzero(np.isfinite(window).all(axis=1))
        order = matlab_sort(first_edition_expected(window[has]))
        _hold(positions, t, has, order, MATLAB_LONGS)
    with np.errstate(invalid="ignore"):
        daily = smartsum(backshift(1, positions) * returns, axis=1)
    return Run(
        name="first-edition MATLAB",
        positions=positions,
        daily=daily,
        annual=float(smartmean(daily)) * TRADING_DAYS,
        stdev=math.nan,
        sharpe=math.nan,
    )


def matlab_sharpe(daily: np.ndarray, std: Callable = smartstd_book_two) -> float:
    """``sqrt(252)*smartmean(ret,1)/smartstd(ret,1)``, with the ``smartstd`` named."""
    return float(math.sqrt(TRADING_DAYS) * smartmean(daily) / std(daily))


def revised_matlab(closes: pd.DataFrame) -> Run:
    """The revised edition's MATLAB, which prints ``AvgAnnRet=0.020205 Sharpe=0.211120``."""
    prices = closes.ffill().to_numpy(dtype=float)  # fillMissingData(cl)
    returns = matlab_returns(prices)
    positions = np.zeros_like(prices)
    for t in range(LOOKBACK + 1, len(prices)):  # for t=lookback+2:end_index
        window = returns[t - LOOKBACK : t].T  # dailyret(t-lookback:t-1,:)'
        has = np.flatnonzero(np.isfinite(window).all(axis=1))
        expected = revised_matlab_expected(window[has], returns[t, has])
        _hold(positions, t, has, matlab_sort(expected), MATLAB_LONGS)
    held = backshift(1, positions)
    with np.errstate(invalid="ignore", divide="ignore"):
        daily = smartsum(held * returns, axis=1) / smartsum(np.abs(held), axis=1)
    return Run(
        name="revised MATLAB",
        positions=positions,
        daily=daily,
        annual=float(smartmean(daily)) * TRADING_DAYS,
        stdev=math.nan,
        sharpe=matlab_sharpe(daily),
    )


def revised_python(
    closes: pd.DataFrame,
    *,
    ranking: Callable[[np.ndarray], np.ndarray] = python_expected,
    longs: slice = PYTHON_LONGS,
    every_row: bool = True,
    clears_first_book: bool = True,
) -> Run:
    """``example7_4.py``, which prints 0.0405…, 0.0700… and 0.5787….

    The keywords default to the printout. ``ranking=summed_returns`` ranks on
    momentum directly, ``longs=MATLAB_LONGS`` buys the top 50, and ``every_row=False`` takes
    the mean and spread over the days that trade, and ``clears_first_book=False``
    leaves out ``positionsTable[capital==0,]=0``. Each exists to say what one
    of the printout's choices does to its figures.
    """
    filled = closes.ffill()  # df.fillna(method='ffill')
    returns = filled.pct_change(fill_method=None).to_numpy(dtype=float)
    positions = np.zeros(filled.shape)
    for t in range(LOOKBACK + 1, len(filled)):  # np.arange(lookback+1, end_index)
        window = returns[t - LOOKBACK + 1 : t].T  # dailyret.iloc[t-lookback+1:t,].T
        has = np.flatnonzero(~np.isnan(window).any(axis=1))
        order = ranking(window[has]).argsort()
        _hold(positions, t, has, order, longs)
    capital = np.nansum(np.abs(backshift(1, positions)), axis=1)
    if clears_first_book:
        positions[capital == 0] = 0  # positionsTable[capital==0,]=0, which clears the first book
    capital[capital == 0] = 1
    daily = np.nansum(backshift(1, positions) * returns, axis=1) / capital
    rows = daily if every_row else daily[_traded(positions)]
    annual = float(np.nanmean(rows)) * TRADING_DAYS
    stdev = float(np.nanstd(rows)) * math.sqrt(TRADING_DAYS)
    return Run("revised Python", positions, daily, annual, stdev, annual / stdev)


def revised_r_reading(closes: pd.DataFrame, *, fill: bool) -> Run:
    """The revised edition's R, read rather than run, which prints the Python's figures.

    Two readings, because the printed code is ambiguous in one place and
    unprinted in another.

    1. ``na.fill(cl, type="locf", nan=NA, fill=NA)`` replaces each missing
       close with NA under zoo's signature, which fills nothing. That is
       ``fill=False``. Its ``type="locf"`` suggests a forward fill was meant,
       which is ``fill=True``.
    2. ``calculateReturns(mycls, 1)`` is taken as each day's percentage change.

    ``dailyret[is.nan(dailyret)] <- 0`` zeroes a 0/0 and leaves an NA, and the
    file holds no close at or below zero, so every missing return stays
    missing here. The PCA and ``lm`` are not carried, because ``lm`` fits an
    intercept and the summed fitted values are the summed returns, as
    :func:`python_expected` says.
    """
    frame = closes.ffill() if fill else closes
    returns = matlab_returns(frame.to_numpy(dtype=float))
    positions = np.zeros(frame.shape)
    for t in range(LOOKBACK + 1, len(frame)):  # for (it in (lookback+2):end_loop)
        window = returns[t - LOOKBACK + 2 : t + 1].T  # dailyret[(it-lookback+2):it,]
        has = np.flatnonzero(np.isfinite(window).all(axis=1))  # complete.cases(t(R))
        order = np.argsort(summed_returns(window[has]), kind="stable")
        _hold(positions, t, has, order, R_LONGS)
    held = backshift(1, positions)
    capital = np.nansum(np.abs(held), axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        daily = np.nansum(held * returns, axis=1) / capital
    kept = daily[np.isfinite(daily)]  # mean(ret, na.rm = TRUE)
    annual = float(kept.mean()) * TRADING_DAYS
    stdev = float(kept.std(ddof=1)) * math.sqrt(TRADING_DAYS)
    name = "revised R, forward-filled" if fill else "revised R, unfilled"
    return Run(name, positions, daily, annual, stdev, annual / stdev)


def without(program: Callable[[pd.DataFrame], Run], closes: pd.DataFrame, symbol: str) -> Run:
    """``program`` run on every column but ``symbol``."""
    return program(closes.drop(columns=[symbol]))


@dataclass(frozen=True)
class Agreement:
    """How far two programs' books agree on the days both hold one.

    ``fewest_differing`` is the smallest number of position cells, out of every
    stock on every shared day, in which the two books disagree on one day.
    """

    days: int
    identical: int
    share: float
    fewest_differing: int


def agreement(a: Run, b: Run) -> Agreement:
    """Days both hold a book, days the books are identical, and the mean share of ``a``'s names
    ``b`` holds the same way."""
    both = (np.abs(a.positions).sum(axis=1) > 0) & (np.abs(b.positions).sum(axis=1) > 0)
    rows = np.flatnonzero(both)
    same = a.positions[rows] == b.positions[rows]
    held = a.positions[rows] != 0
    return Agreement(
        days=len(rows),
        identical=int(same.all(axis=1).sum()),
        share=float(((held & same).sum(axis=1) / held.sum(axis=1)).mean()),
        fewest_differing=int((~same).sum(axis=1).min()),
    )


# --- verdicts ------------------------------------------------------------------


def prints_as(value: float, printed: str) -> bool:
    """Whether ``value`` formats to ``printed`` at the number of decimals it carries."""
    decimals = len(printed.split(".")[1])
    return f"{value:.{decimals}f}" == printed


def within(values: tuple[float, ...], printed: tuple[str, ...]) -> bool:
    """Whether each value is within :data:`DIGITS_17` of the figure printed beside it."""
    return all(abs(v - float(p)) < DIGITS_17 for v, p in zip(values, printed, strict=True))


def _figures(run: Run) -> tuple[float, float, float]:
    return (run.annual, run.stdev, run.sharpe)


def verdict(reproduced: bool) -> str:
    return "reproduced" if reproduced else "did not reproduce"


# --- the report ------------------------------------------------------------------


@dataclass(frozen=True)
class Results:
    """Every run the report prints."""

    first: Run
    matlab: Run
    python: Run
    r_unfilled: Run
    r_filled: Run
    python_fifty: Run
    python_traded: Run
    python_first_book: Run
    momentum: Run
    first_unspliced: Run
    matlab_unspliced: Run
    python_unspliced: Run


def compute(closes: pd.DataFrame) -> Results:
    """Run every printout, the variants that separate them, and each without :data:`SPLICED`."""
    return Results(
        first=first_edition_matlab(closes),
        matlab=revised_matlab(closes),
        python=revised_python(closes),
        r_unfilled=revised_r_reading(closes, fill=False),
        r_filled=revised_r_reading(closes, fill=True),
        python_fifty=revised_python(closes, ranking=summed_returns, longs=MATLAB_LONGS),
        python_traded=revised_python(closes, ranking=summed_returns, every_row=False),
        python_first_book=revised_python(closes, ranking=summed_returns, clears_first_book=False),
        momentum=revised_python(closes, ranking=summed_returns),
        first_unspliced=without(first_edition_matlab, closes, SPLICED),
        matlab_unspliced=without(revised_matlab, closes, SPLICED),
        python_unspliced=without(
            lambda frame: revised_python(frame, ranking=summed_returns), closes, SPLICED
        ),
    )


def report(members: list[VintageEntry], closes: pd.DataFrame, results: Results) -> None:
    """Print each printout beside what Chan printed, what separates them, and the verdicts."""
    r = results
    print("The PCA factor model, Chan's Example 7.4 in Quantitative Trading")
    print(f"  closes   {panel_line(members)}")
    print(
        f"  file     {closes.index[0].date()} to {closes.index[-1].date()}, "
        f"{len(closes)} days, {closes.shape[1]} stocks"
    )
    print(
        f"  rule     lookback {LOOKBACK}, {FACTORS} factors, short the {TOP_N} lowest expected "
        "returns and buy the highest, no cost"
    )
    print()
    print(f"  {'Printout':<24} {'Figure':<30} {'Computed':>20} {'Chan prints':>20}")
    rows = [
        (r.first.name, "annual mean, sum over positions", r.first.annual, FIRST_EDITION_PRINTS),
        (r.matlab.name, "annual mean return", r.matlab.annual, REVISED_MATLAB_PRINTS[0]),
        (r.matlab.name, "Sharpe ratio", r.matlab.sharpe, REVISED_MATLAB_PRINTS[1]),
    ]
    printouts = ((r.python, PYTHON_PRINTS), (r.r_unfilled, R_PRINTS), (r.r_filled, R_PRINTS))
    for each, printed in printouts:
        for label, value, chan in zip(
            ("annual mean return", "annualised std", "Sharpe ratio"),
            _figures(each),
            printed,
            strict=True,
        ):
            rows.append((each.name, label, value, chan))
    for name, label, value, chan in rows:
        print(f"  {name:<24} {label:<30} {value:>20.17g} {chan:>20}")
    print(
        f"  The book: {BOOK_MATLAB_PERCENT}% a year in MATLAB and {BOOK_PYTHON_R_PERCENT}% in "
        "Python and R, location 4051."
    )
    print()
    first_ok = prints_as(r.first.annual, FIRST_EDITION_PRINTS)
    matlab_ok = prints_as(r.matlab.annual, REVISED_MATLAB_PRINTS[0]) and prints_as(
        r.matlab.sharpe, REVISED_MATLAB_PRINTS[1]
    )
    python_ok = within(_figures(r.python), PYTHON_PRINTS)
    r_ok = within(_figures(r.r_unfilled), R_PRINTS) or within(_figures(r.r_filled), R_PRINTS)
    together = agreement(r.matlab, r.python)
    # The printed Python buys 49 and the MATLAB 50, so their books can never be
    # identical. Round-off is judged against the Python given 50 longs, whose
    # books are the MATLAB's size.
    sized = agreement(r.matlab, r.python_fifty)
    print("  Verdicts")
    print(f"    first-edition MATLAB   {verdict(first_ok)}")
    print(f"    revised MATLAB         {verdict(matlab_ok)}")
    print(f"    revised Python         {verdict(python_ok)}")
    print(
        f"    revised R              {verdict(r_ok)}, under either reading. Its printed "
        "figures are the Python's."
    )
    holds = sized.identical == sized.days
    print(
        f"    'round off errors'     {'holds' if holds else 'does not hold'}. With {TOP_N} longs "
        f"each, the revised books are identical on {sized.identical} of {sized.days} days,"
    )
    print(
        f"                           and differ in at least {sized.fewest_differing} positions "
        "on every one."
    )
    print()
    print("  What separates 2% from 4%")
    momentum_same = bool((r.python.positions == r.momentum.positions).all())
    print(
        f"    The Python's book ranked on summed returns alone is "
        f"{'identical on every day' if momentum_same else 'different'}."
    )
    print(
        f"    On average {together.share:.2%} of the revised MATLAB's names are held the same way "
        f"by the Python, and {sized.share:.2%} with {TOP_N} longs."
    )
    print(
        f"    The Python with {TOP_N} longs: {r.python_fifty.annual:.4f} a year, "
        f"Sharpe ratio {r.python_fifty.sharpe:.4f}."
    )
    print(
        f"    The Python over its {int(r.python.traded.sum())} trading days: "
        f"{r.python_traded.annual:.4f} a year, Sharpe ratio {r.python_traded.sharpe:.4f}."
    )
    print(
        f"    The Python keeping its first book: {r.python_first_book.annual:.4f} a year, "
        f"Sharpe ratio {r.python_first_book.sharpe:.4f}."
    )
    first_traded = float(smartmean(r.first.daily[r.first.traded])) * TRADING_DAYS
    print(
        f"    The first edition over its {int(r.first.traded.sum())} trading rows: "
        f"{first_traded:.4f}."
    )
    print(
        "    The revised MATLAB's Sharpe ratio under the first edition's smartstd: "
        f"{matlab_sharpe(r.matlab.daily, smartstd_first_edition):.4f}."
    )
    print()
    print(f"  Without {SPLICED}, whose two price histories forward-fill into one day's return")
    print(f"    first-edition MATLAB   {r.first_unspliced.annual:.4f}")
    print(
        f"    revised MATLAB         {r.matlab_unspliced.annual:.4f}, "
        f"Sharpe ratio {r.matlab_unspliced.sharpe:.4f}"
    )
    print(
        f"    revised Python         {r.python_unspliced.annual:.4f}, "
        f"Sharpe ratio {r.python_unspliced.sharpe:.4f}"
    )
    print()
    print(
        "  The file holds only the companies in the index on 2008-01-14, "
        "so every figure above is about survivors."
    )
    print(
        "  Exploratory. Reproducing Chan's figures spends the 2004 to 2008 sample on a rule he "
        "chose, so this says whether"
    )
    print(
        "  his numbers reproduce on his file and nothing about whether a factor model earns money. "
        "docs/replication-log.md Entry 13 carries the verdicts."
    )


def run(data_dir: Path | None = None) -> Results:
    """Read the S&P 600 file, run every printout and print the report."""
    members, closes = load_panel(SMALL_CAPS, field="Close", data_dir=data_dir)
    results = compute(closes)
    report(members, closes, results)
    return results


def main() -> None:
    argparse.ArgumentParser(
        description="Chan's PCA factor model, Example 7.4, on his S&P 600 file"
    ).parse_args()
    try:
        run()
    except VintageUnavailable as refused:
        # A refusal naming the missing member is worth nothing at the bottom of
        # a traceback, so it reaches the reader as one line, the way
        # chan.pead.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
