"""Heinrich's closed-form moments of a Pearson type IV, written apart from the module that fits one.

:func:`chan.tu_hypothesis_tests.pearson_iv_parameters` turns four moments into
type IV's four parameters. The check on that is the reverse map, written
independently, so a mistake in one does not hide in the other.
``tests/test_tu_hypothesis_tests.py`` and ``tests/test_monte_carlo_leverage.py``
both hold the fit to it, on TU's moments and on Example 5.1's returns, so it
lives here once rather than in each.

The formulas are Heinrich (2004), "A guide to the Pearson type IV
distribution", CDF/MEMO/STATISTICS/PUBLIC/6820, with r = 2(m − 1). The mean
exists for m > 1, the standard deviation for m > 3/2, the skewness for m > 2
and the kurtosis for m > 5/2.
"""

from __future__ import annotations

import math


def closed_form_moments(
    m: float, nu: float, a: float, lam: float
) -> tuple[float, float, float, float]:
    """The mean, standard deviation, skewness and kurtosis, not in excess form, of type IV."""
    r = 2 * (m - 1)
    q = r * r + nu * nu
    mean = lam - a * nu / r
    std = math.sqrt(a * a * q / (r * r * (r - 1)))
    skewness = -4 * nu / (r - 2) * math.sqrt((r - 1) / q)
    kurt = 3 * (r - 1) * ((r + 6) * q - 8 * r * r) / ((r - 2) * (r - 3) * q)
    return mean, std, skewness, kurt
