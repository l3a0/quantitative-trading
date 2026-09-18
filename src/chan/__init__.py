"""Experiments and replications from Ernest Chan's quantitative trading books.

Every result this package produces names the data vintage it ran on, or says
it has none. A vendor restates an adjusted price series without announcing it,
so a number computed from a series downloaded today is not the number the same
code produced last year. Recording the vintage is what makes a result
checkable later.

The exception is a result computed from nothing. ``coin_flip_growth`` works a
gamble, so it has no vendor and no download date and nothing to restate, and
it says so where every other run names a file. ``pair_cointegration``'s
``--selftest`` is the same shape at a smaller scale.
"""

__all__: list[str] = []
