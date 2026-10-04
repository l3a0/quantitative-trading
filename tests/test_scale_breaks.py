"""The pins for the guard: which committed series change scale, and what stops on one.

A verified vintage is not the same thing as a series it is safe to compute
across. The bytes can be exactly what the manifest recorded while the series
means one thing before a day and another after it, and ``ko_chan.csv`` is that
case rather than a hypothetical. So these cases hold two claims. The guard
reads each committed price series against itself and reports the days it
changed scale, and a run whose window spans one of those days stops instead of
printing a number.

The case order is the order the rules appear on
[issue 3](https://github.com/l3a0/quantitative-trading/issues/3), which is the
convention ``tests/test_vintage.py`` states for itself against issue 1.

This is its own file rather than more of ``tests/test_series.py``, whose
subject is which vintage a run resolves and that it is that one, or of
``tests/test_vintage.py``, whose every case is driven by a synthetic series.
A guard over every committed price vintage is neither, and the repo's shape is one file
per concern.

Every refusal is asserted on its message and not only on its type. Absent,
unreadable, altered and never-recorded are the four ``tests/test_series.py``
tells apart, and a window crossing a scale break is a fifth problem with a
fifth fix.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from chan import paths
from chan.series import (
    SCALE_BREAK_BOUND,
    WindowCrossesScaleBreak,
    _holds_minute_bars,
    _parse_close,
    aligned_closes,
    load_minute_close,
    load_vintage,
    minute_close,
    refuse_window_crossing_a_break,
    scale_breaks,
)
from chan.vintage import (
    MANIFEST_NAME,
    PRICES,
    VintageEntry,
    VintageUnavailable,
    read_manifest,
    read_vintage,
    record_vintage,
)
from tests.support.committed_pairs import adjusted_against_raw
from tests.support.committed_vintages import committed_copy as copy_the_committed_tree
from tests.support.committed_vintages import in_a_lifted_source, rewrite_entry

#: The breaks the single-series vintages carry, recorded rather than failing.
#:
#: Two day-over-day moves in ``ko_chan.csv`` are near-exact halvings, 1.0100 to
#: 0.5100 across 1965-02-19 at a ratio of 0.5050 and 1.0700 to 0.5400 across
#: 1968-06-03 at 0.5047. They are real, so the guard's first run on `main` is
#: red unless they are written down, and this is where they are written down.
#: That they are 2:1 splits is the obvious reading and is not verified here,
#: because nothing in this repo holds a corporate-action feed. The finding does
#: not rest on the label: a near-exact halving is a scale break whichever it
#: was.
#:
#: Nothing computes across them. The KO/PEP replication reads the intersection
#: with ``pep_chan.csv``, which starts 1977-01-03, so both breaks fall outside
#: every window anything reads, which
#: ``TestAWindowThatCrossesABreakStops`` runs rather than asserts in prose.
#: Recording the fact beside the data is
#: [issue 108](https://github.com/l3a0/quantitative-trading/issues/108).
KNOWN_BREAKS = {"ko_chan.csv": ["1965-02-19", "1968-06-03"]}

#: What the guard flags in the price columns of Chan's stock, ETF and strip files.
#:
#: Four stock files and the ETF file account for every flag here. His continuous
#: futures saves and ``VIX.csv`` flag more, which ``FLAGGED_IN_CHANS_FUTURES``
#: pins. The futures strips and the gold
#: series, 1,232 columns, flag nothing, which ``tests/test_futures_strips.py``
#: says on its own.
#:
#: Pinned by path and day rather than as a count, so a day that stops being
#: flagged fails as surely as a new one. These are flags rather than known
#: breaks. Each is a close below 0.625 or above 1.6 times the one before, a
#: bound fitted to the single-series vintages, and most are real moves in
#: single stocks: AAPL at 0.4813 on 2000-09-29, its profit-warning day, and the
#: energy names of July 2002 among them.
#:
#: Three are not price moves at all. ``spx_20071123/wyn.csv`` and
#: ``spx_20071123/dfs.csv`` each hold two companies under one symbol across a
#: gap of 952 and 400 trading days, ``ijr_20080114/pmc.csv`` holds two price
#: histories across a gap of 851, and a member's own rows read each gap as one
#: day. Four sit within 0.02 of a two-for-one split, and whether any is
#: an unadjusted split is not known: AES and AYE here, and CBU and INSP in the
#: S&P 600 file. AAPL's column absorbs its June 2000 split with no jump, so its
#: day is the move it looks like. The book-two S&P 500 file adds 30 days in 17
#: stocks, every one between 2007 and 2009 and most of them banks and insurers
#: in the 2008 crisis, such as AIG on 2008-09-15. None falls in the 2011 and 2012
#: window Example 7.2 trades, all 30 fall in Example 4.1's, which is the file's
#: whole span, and none sits near a split, measured on
#: [issue 250](https://github.com/l3a0/quantitative-trading/issues/250). ``data/README.md`` and
#: [issue 88](https://github.com/l3a0/quantitative-trading/issues/88) carry
#: the measurements. Whether a run reading one of these files refuses a window
#: crossing a flagged day is for that run to decide.
#:
#: The later S&P 600 save, ``ijr_20080131/``, flags 21 days in 19 stocks,
#: committed under
#: [issue 225](https://github.com/l3a0/quantitative-trading/issues/225). Of
#: the 18 stocks the earlier save flags, 17 flag the same days. INSP's flag
#: moves from 2008-01-09 to 2008-01-07, because the later save rescales
#: INSP's closes on 2008-01-07 and 2008-01-08 by 0.4969 and leaves the days
#: before them alone. IDXX is new, and its two days are one close: 30.05 on
#: 2008-01-25, between 55.60 and 53.75, equal to that day's low and far below
#: its open of 55.28. Example 7.6 reads neither stock on those days, because
#: its January 2008 holding reads the closes of 2007-12-31 and 2008-01-31.
#:
#: [Issue 17](https://github.com/l3a0/quantitative-trading/issues/17) decided
#: it for Example 3.7, and ``chan.khandani_lo``'s docstring says why it does
#: not call the guard: Chan's rule puts a weight of 0 on every return that is
#: not finite, and handed the panel the guard refuses over ten missing closes
#: rather than over any scale break.
#: ``TestTheScaleBreakDecision`` in ``tests/test_khandani_lo.py`` runs both of
#: its answers, on the closes and on the opens.
#:
#: [Issue 206](https://github.com/l3a0/quantitative-trading/issues/206)
#: inherited that decision for Example 3.8's rule B, which reads the opens with
#: the same rule and the same NaN mask. Its rule A, Chan's Python notebook,
#: fills each gap with the last price and so reads WYN's restart as a return of
#: 121.5 on the closes and 127.65 on the opens. That is the notebook's own
#: computation rather than a window to refuse, and ``TestRuleAOnTheCloses`` and
#: ``TestRuleAOnTheOpens`` in the same file pin it.
#:
#: [Issue 18](https://github.com/l3a0/quantitative-trading/issues/18) decided
#: that ``chan.equity_seasonals`` refuses no window for Examples 7.6 and 7.7. Its
#: job is to reproduce what Chan printed, and Chan's scripts ran on these closes
#: as they stand, so a guard would refuse the computation being reproduced.
#: AAPL's 2000-09-29 is a month-end, so Example 7.7 ranks that day's move as
#: AAPL's September 2000 return. WYN and DFS, the two symbols that each hold
#: two companies, leak no false move into it, because no finite monthly return
#: reaches across either gap. ``TestTheShapesTheScaleBreakCommentNames`` in
#: ``tests/test_equity_seasonals.py`` holds both claims. Example 7.6's revised
#: Python forward-fills its year-end closes, so its 2007 ranking reads PMC's
#: 851-day gap as a return of 1.3056 and holds PMC short in January 2008.
#: That is the printed program's computation, and ``TestJanuaryPython`` pins
#: it and the figure without the fill.
#:
#: [Issue 20](https://github.com/l3a0/quantitative-trading/issues/20) decided
#: that ``chan.pead`` calls the guard for Example 7.2, on each stock's opens
#: and closes from its first price onward. The book-two S&P 500 file's 30 flagged days
#: all fall in 2007 to 2009, and the window is 2011-01-03 to 2012-04-24, so
#: nothing in it is refused. Reading from the first price is what lets MPC and
#: XYL, spun off inside the window, pass without a missing price after that
#: being dropped. ``TestTheRefusals`` in ``tests/test_pead.py`` runs the guard
#: on the committed file and on both shapes.
#:
#: [Issue 21](https://github.com/l3a0/quantitative-trading/issues/21) decided
#: that ``chan.pca_factor`` refuses no window for Example 7.4, for the reason
#: issue 18 gives: every printout forward-fills these closes as they stand, so
#: a guard would refuse the computation being reproduced. PMC, flagged below on
#: 2007-08-01, is two price histories under one symbol with 851 days missing
#: between them, and the fill reads that gap as one day's return of 1.8654.
#: ``TestTheSplice`` in ``tests/test_pca_factor.py`` pins that return and every
#: printout's figures without PMC.
#:
#: [Issue 22](https://github.com/l3a0/quantitative-trading/issues/22) decided
#: that ``chan.momentum_factor`` refuses no window either. Apart from WYN's and
#: DFS's restarts, the flags on the S&P 500 file read as real moves, and a
#: momentum ranking is meant to see a real collapse. Refusing a window across
#: AAPL's 2000-09-29 would drop exactly the kind of loser the factor exists to
#: short. WYN and DFS cannot reach a formation across their gaps, because a
#: stock enters one only with a finite close at all 14 month-ends from t − 12
#: to t + 1, and each gap holds a month-end with no close.
#: ``TestTheScaleBreakDecision`` in ``tests/test_momentum_factor.py`` holds
#: that.
#:
#: [Issue 295](https://github.com/l3a0/quantitative-trading/issues/295) decided
#: that ``chan.buy_on_gap`` refuses no window for *Algorithmic Trading*'s
#: Example 4.1, on the reasoning issues 18, 21 and 22 give. Its window is the
#: book-two S&P 500 file's whole span, 2006-05-11 to 2012-04-24, so it holds all 30
#: of that file's flagged days, and the guard ``chan.pead`` calls would refuse
#: the run. ``bog.m`` ran on these prices as they stand, and none of the 30 sits
#: near a split. One position lands on one, a short in MS on 2008-10-13 under
#: the mirror the issue declared. ``TestTheScaleBreakDecision`` in
#: ``tests/test_buy_on_gap.py`` runs the guard and holds both facts.
#:
#: [Issue 297](https://github.com/l3a0/quantitative-trading/issues/297) decided
#: that ``chan.cross_sectional_momentum`` refuses no window for *Algorithmic
#: Trading*'s Example 6.2, on issue 22's reasoning. The book-two S&P 500 file's 30
#: flagged stock-days fall one inside the 2007 window, ETFC's 2007-11-12, and
#: 29 inside 2008 and 2009, so the guard would refuse both windows the book
#: prints, and ``kentdaniel.m`` ran across them as they stand. No stock in that
#: file has a missing price after its first, so no ranking return reaches
#: across a gap. ``TestTheScaleBreakDecision`` in
#: ``tests/test_cross_sectional_momentum.py`` runs the guard and holds both.
#:
#: [Issue 296](https://github.com/l3a0/quantitative-trading/issues/296) decided
#: that ``chan.khandani_lo_book_two`` refuses no window for *Algorithmic
#: Trading*'s Examples 4.3 and 4.4. Their window,
#: 2007-01-03 to 2011-12-30, spans all 30 of the book-two S&P 500 file's flagged days,
#: and the guard refuses it on 17 stocks' closes and 14 stocks' opens. Chan's
#: script computes across them and his figures reproduce only with them in.
#: Most read as the 2008 crisis. CAH's 2009-09-02 does not, and without CAH
#: neither of Example 4.3's figures lands. ``TestTheScaleBreakDecision`` in
#: ``tests/test_khandani_lo_book_two.py`` runs both refusals and pins CAH.
#:
#: [Issue 299](https://github.com/l3a0/quantitative-trading/issues/299) lifted
#: Chan's book-two ETF file, and the guard flags 58 days in 8 of its 67 ETFs,
#: every one a leveraged or inverse fund and every day between 2008-04-16 and
#: 2009-06-25. EDC, MWJ and SMN are among the eight, and they hold the file's
#: 11 closes below zero. A dividend subtracted in dollars rather than rescaled
#: is what lets a close go below zero, which
#: ``TestTheETFFileSubtractsEachDividend`` in ``tests/test_series.py`` pins. No
#: run reads this file yet, so no decision about refusing a window has been
#: made, and no experiment issue 299 names reads any of the eight.
FLAGGED_IN_CHANS_MAT_FILES = {
    "ijr_20080114/agp.csv": ["2005-09-29"],
    "ijr_20080114/bbx.csv": ["2007-10-26"],
    "ijr_20080114/bcsi.csv": ["2006-02-06"],
    "ijr_20080114/blti.csv": ["2007-11-06"],
    "ijr_20080114/cbm.csv": ["2007-05-04"],
    "ijr_20080114/cbu.csv": ["2004-04-13"],
    "ijr_20080114/cybx.csv": ["2004-06-16", "2004-08-12"],
    "ijr_20080114/ditc.csv": ["2005-05-27"],
    "ijr_20080114/insp.csv": ["2008-01-09"],
    "ijr_20080114/ivac.csv": ["2004-07-13"],
    "ijr_20080114/mag.csv": ["2005-05-04"],
    "ijr_20080114/matk.csv": ["2005-04-28"],
    "ijr_20080114/moh.csv": ["2005-07-21"],
    "ijr_20080114/odsy.csv": ["2004-10-18"],
    "ijr_20080114/pmc.csv": ["2007-08-01"],
    "ijr_20080114/poss.csv": ["2004-08-24"],
    "ijr_20080114/rgr.csv": ["2007-10-25"],
    "ijr_20080114/scur.csv": ["2006-07-12"],
    "ijr_20080131/agp.csv": ["2005-09-29"],
    "ijr_20080131/bbx.csv": ["2007-10-26"],
    "ijr_20080131/bcsi.csv": ["2006-02-06"],
    "ijr_20080131/blti.csv": ["2007-11-06"],
    "ijr_20080131/cbm.csv": ["2007-05-04"],
    "ijr_20080131/cbu.csv": ["2004-04-13"],
    "ijr_20080131/cybx.csv": ["2004-06-16", "2004-08-12"],
    "ijr_20080131/ditc.csv": ["2005-05-27"],
    "ijr_20080131/idxx.csv": ["2008-01-25", "2008-01-28"],
    "ijr_20080131/insp.csv": ["2008-01-07"],
    "ijr_20080131/ivac.csv": ["2004-07-13"],
    "ijr_20080131/mag.csv": ["2005-05-04"],
    "ijr_20080131/matk.csv": ["2005-04-28"],
    "ijr_20080131/moh.csv": ["2005-07-21"],
    "ijr_20080131/odsy.csv": ["2004-10-18"],
    "ijr_20080131/pmc.csv": ["2007-08-01"],
    "ijr_20080131/poss.csv": ["2004-08-24"],
    "ijr_20080131/rgr.csv": ["2007-10-25"],
    "ijr_20080131/scur.csv": ["2006-07-12"],
    "inputdata_etf/edc.csv": [
        "2009-01-20",
        "2009-02-17",
        "2009-02-23",
        "2009-02-24",
        "2009-03-02",
        "2009-03-03",
        "2009-03-04",
        "2009-03-05",
        "2009-03-06",
        "2009-03-09",
        "2009-03-10",
        "2009-03-23",
        "2009-03-30",
    ],
    "inputdata_etf/eev.csv": ["2008-10-13", "2008-10-28"],
    "inputdata_etf/fas.csv": ["2008-12-01", "2009-01-20"],
    "inputdata_etf/faz.csv": ["2008-11-24", "2009-03-10", "2009-03-23", "2009-04-09"],
    "inputdata_etf/mwj.csv": [
        "2009-02-23",
        "2009-02-24",
        "2009-03-02",
        "2009-03-03",
        "2009-03-04",
        "2009-03-05",
        "2009-03-10",
        "2009-03-11",
        "2009-03-12",
        "2009-03-17",
        "2009-03-23",
    ],
    "inputdata_etf/mwn.csv": ["2009-06-25"],
    "inputdata_etf/smn.csv": [
        "2008-04-16",
        "2008-05-15",
        "2008-05-16",
        "2008-05-19",
        "2008-05-20",
        "2008-05-21",
        "2008-05-28",
        "2008-05-29",
        "2008-06-05",
        "2008-06-06",
        "2008-06-09",
        "2008-06-10",
        "2008-06-11",
        "2008-06-13",
        "2008-06-16",
        "2008-06-17",
        "2008-06-18",
        "2008-06-19",
        "2008-06-20",
        "2008-06-23",
        "2008-06-24",
        "2008-06-26",
        "2008-07-02",
        "2008-10-13",
    ],
    "inputdata_etf/tna.csv": ["2008-12-01"],
    "inputdataohlcdaily_stocks_20120424/aig.csv": [
        "2008-09-15",
        "2008-09-17",
        "2009-03-16",
        "2009-08-05",
    ],
    "inputdataohlcdaily_stocks_20120424/c.csv": ["2009-02-27"],
    "inputdataohlcdaily_stocks_20120424/cah.csv": ["2009-09-02"],
    "inputdataohlcdaily_stocks_20120424/cbg.csv": ["2009-03-25"],
    "inputdataohlcdaily_stocks_20120424/cvh.csv": ["2008-10-22"],
    "inputdataohlcdaily_stocks_20120424/etfc.csv": ["2007-11-12"],
    "inputdataohlcdaily_stocks_20120424/fitb.csv": ["2008-09-29", "2009-02-06"],
    "inputdataohlcdaily_stocks_20120424/gnw.csv": [
        "2008-09-19",
        "2008-09-29",
        "2008-09-30",
        "2008-10-13",
        "2008-11-07",
        "2008-11-11",
        "2008-11-24",
    ],
    "inputdataohlcdaily_stocks_20120424/har.csv": ["2008-01-14"],
    "inputdataohlcdaily_stocks_20120424/hig.csv": ["2008-10-30", "2008-12-05"],
    "inputdataohlcdaily_stocks_20120424/lnc.csv": ["2008-11-19", "2009-03-30"],
    "inputdataohlcdaily_stocks_20120424/mos.csv": ["2008-10-02"],
    "inputdataohlcdaily_stocks_20120424/ms.csv": ["2008-10-13"],
    "inputdataohlcdaily_stocks_20120424/pnc.csv": ["2009-01-20"],
    "inputdataohlcdaily_stocks_20120424/rf.csv": ["2008-09-29"],
    "inputdataohlcdaily_stocks_20120424/stt.csv": ["2009-01-20"],
    "inputdataohlcdaily_stocks_20120424/xl.csv": ["2008-10-09", "2009-02-11"],
    "spx_20071123/aapl.csv": ["2000-09-29"],
    "spx_20071123/aes.csv": ["2001-09-26"],
    "spx_20071123/anf.csv": ["2000-02-16"],
    "spx_20071123/aye.csv": ["2002-10-08"],
    "spx_20071123/bby.csv": ["2000-11-09"],
    "spx_20071123/biib.csv": ["2005-02-28"],
    "spx_20071123/brl.csv": ["2000-08-09"],
    "spx_20071123/ca.csv": ["2000-07-05"],
    "spx_20071123/ci.csv": ["2002-10-25"],
    "spx_20071123/cnp.csv": ["2002-07-23", "2002-07-25"],
    "spx_20071123/cof.csv": ["2002-07-17"],
    "spx_20071123/cpwr.csv": ["2000-04-12"],
    "spx_20071123/csc.csv": ["2001-03-16"],
    "spx_20071123/ctxs.csv": ["2000-06-12"],
    "spx_20071123/dfs.csv": ["2007-07-02"],
    "spx_20071123/duk.csv": ["2001-01-29"],
    "spx_20071123/dyn.csv": ["2002-07-23", "2002-07-25", "2002-07-29", "2002-11-19"],
    "spx_20071123/eds.csv": ["2002-09-19"],
    "spx_20071123/etfc.csv": ["2007-11-12"],
    "spx_20071123/etn.csv": ["2001-01-02"],
    "spx_20071123/gas.csv": ["2002-07-19"],
    "spx_20071123/hal.csv": ["2001-12-07"],
    "spx_20071123/novl.csv": ["2000-05-03"],
    "spx_20071123/q.csv": ["2002-06-26"],
    "spx_20071123/see.csv": ["2002-07-30"],
    "spx_20071123/thc.csv": ["2002-11-08"],
    "spx_20071123/tie.csv": ["2001-09-17"],
    "spx_20071123/uis.csv": ["2000-06-29"],
    "spx_20071123/unm.csv": ["2000-02-10"],
    "spx_20071123/vrsn.csv": ["2002-04-26"],
    "spx_20071123/wfr.csv": ["2001-08-10", "2001-09-28", "2001-10-01"],
    "spx_20071123/wmb.csv": ["2002-07-22", "2002-07-23", "2002-07-29"],
    "spx_20071123/wpi.csv": ["2001-11-13"],
    "spx_20071123/wyn.csv": ["2001-09-17", "2006-08-01"],
}

#: The days ZB, the 30-year bond, closes off its scale in Chan's continuous futures saves.
#:
#: [Issue 313](https://github.com/l3a0/quantitative-trading/issues/313) lifted
#: four saves, and the three 2,000-row ones flag the same 33 days in ZB and the
#: same 9 in ZF, between 1995-12-05 and 2008-04-16, with closes as low as
#: 0.4844. Up to 1998-03-10 ZB runs from 0.4844 to 5.1094 and ZF from 1.3594
#: to 3.3594, which is not a bond future's scale. The next row in each is
#: 2008-04-16, ten years later, and that flag is the jump across the hole
#: onto the bond's scale. ZN has the same hole but no flag, because it sits on
#: a bond's scale on both sides. No script of Chan's reads any of the three.
#: The 2012-05-04 save starts in 2008-04 and flags nothing.
ZB_FLAGS = [
    "1996-04-16",
    "1996-04-18",
    "1996-04-23",
    "1996-04-25",
    "1996-08-02",
    "1996-08-27",
    "1996-10-03",
    "1996-10-11",
    "1996-10-16",
    "1997-01-24",
    "1997-01-28",
    "1997-01-30",
    "1997-03-11",
    "1997-03-12",
    "1997-05-07",
    "1997-05-08",
    "1997-05-13",
    "1997-05-14",
    "1997-05-15",
    "1997-05-20",
    "1997-05-21",
    "1997-05-22",
    "1997-06-03",
    "1997-06-24",
    "1997-12-17",
    "1997-12-18",
    "1997-12-19",
    "1997-12-31",
    "1998-02-27",
    "1998-03-02",
    "1998-03-03",
    "1998-03-10",
    "2008-04-16",
]

#: The days ZF, the five-year note, closes off its scale in the same three saves.
ZF_FLAGS = [
    "1995-12-05",
    "1995-12-06",
    "1995-12-28",
    "1996-01-10",
    "1996-01-17",
    "1996-03-01",
    "1998-01-09",
    "1998-01-21",
    "2008-04-16",
]

#: Every flag in the continuous futures saves and ``VIX.csv``.
#:
#: VIX's one day is 2007-02-27, when the index closed at 18.31 after 11.15,
#: which is a real move rather than a change of units.
FLAGGED_IN_CHANS_FUTURES = {
    **{
        f"inputdataohlcdaily_{save}/{symbol}.csv": days
        for save in ("20120507", "20120511", "20120517")
        for symbol, days in (("zb", ZB_FLAGS), ("zf", ZF_FLAGS))
    },
    "vix/vix.csv": ["2007-02-27"],
}

#: Every day the guard flags across the manifest.
EVERY_FLAG = {**KNOWN_BREAKS, **FLAGGED_IN_CHANS_MAT_FILES, **FLAGGED_IN_CHANS_FUTURES}

#: A series that halves partway through, and its date index.
#:
#: Four days is the smallest set that carries a break with an ordinary move on
#: either side of it, which is what separates a guard that flags the break from
#: one that flags everything.
DAYS = ["2026-01-02", "2026-01-05", "2026-01-06", "2026-01-07"]
HALVES = [10.0, 10.5, 5.2, 5.3]


def series_of(closes: list[float], *, days: list[str] = DAYS) -> pd.Series:
    """``closes`` as the reader hands a series back, date-indexed and named."""
    return pd.Series(
        closes, index=pd.DatetimeIndex([pd.Timestamp(day) for day in days]), name="ZZZ"
    )


def days_of(flagged: list[pd.Timestamp]) -> list[str]:
    """Flagged timestamps as the ISO dates a pin is written in."""
    return [str(day.date()) for day in flagged]


def price_entries(data_dir: Path | None = None) -> list:
    """Every committed vintage the guard reads, which is every one that holds a price.

    A vintage is kept by its basis rather than by name, so a second rate series
    or a second source of flags recorded later is skipped the day it lands. A
    scale break is a price changing units, such as a split. The design doc's
    **rate** entry says why a rate cannot be read that way, and
    ``test_a_rate_series_would_report_breaks_if_it_were_read_as_a_price``
    measures it on the committed bill series. An ``event`` vintage holds 0 and
    1, which is not a price at all, and a ``return`` vintage holds a strategy's
    returns, which are not one either.
    """
    return [entry for entry in read_manifest(data_dir) if entry.price_basis in PRICES]


def closes_of(entry: VintageEntry, data_dir: Path | None = None) -> pd.Series:
    """One close per day from a committed price vintage, through the reader its bytes need.

    The guard reads one series per day. A file of minute bars is read at 16:59
    by ``minute_close``, which gives the closes Example 2.1 reads, so the guard
    reads those. Every other file goes through ``_parse_close``, which refuses a
    minute file rather than reading its times as closes, so a scan that forgot
    this branch would stop rather than pass.
    """
    payload = read_vintage(entry, data_dir=data_dir)
    if _holds_minute_bars(payload):
        return minute_close(payload, entry)
    return _parse_close(payload, entry.symbol)


def breaks_across_the_manifest(data_dir: Path | None = None) -> dict[str, list[str]]:
    """Every committed price vintage that changes scale inside itself, keyed by its path.

    It iterates the manifest's price vintages through :func:`price_entries`
    rather than a list of the vintages this repo holds today, so a new one is
    covered on the day it is recorded rather than on the day somebody
    remembers to extend a list. That is the
    rule ``TestTheCommittedManifest`` follows in ``tests/test_vintage.py``, and
    the opposite of ``COMMITTED`` in ``tests/test_series.py``.

    It lives here and not in :mod:`chan.series`, because nothing under ``src/``
    has a reason to scan the whole manifest. A run opens the two legs it was
    asked for and the refusal reads those, so a public scan would be a path
    with a count of zero, which is what this repo's ranking directive says not
    to add. What needs it is this file.

    It reaches the bytes through :func:`read_vintage` and the module's own
    parse rather than through :func:`load_vintage`, which resolves an entry it
    was just handed and would stop on the first symbol carrying two downloads
    of one basis. That state is what
    [issue 83](https://github.com/l3a0/quantitative-trading/issues/83) brings.

    Keyed by the entry's path and not by the entry, since an entry carries a
    field that is not hashable and keying by one reaches an operator as a
    traceback, which is
    [issue 93](https://github.com/l3a0/quantitative-trading/issues/93).
    """
    found = {}
    for entry in price_entries(data_dir):
        flagged = scale_breaks(closes_of(entry, data_dir))
        if flagged:
            found[entry.path] = days_of(flagged)
    return found


def payload_of(rows: list[tuple[str, str]]) -> bytes:
    """The bytes a recorded vintage holds, with the close left as written text.

    Text rather than a float, because two of the cases below need a close no
    float can carry: a value ``_parse_close`` coerces to NaN, and a negative
    one. Neither survives ``record_vintage``, which is why these are written
    into a manifest by hand the way the hand-written vintages were.
    """
    return ("Date,Close\n" + "".join(f"{day},{close}\n" for day, close in rows)).encode("utf-8")


def place(directory: Path, *, name: str, rows: list[tuple[str, str]]) -> None:
    """Leave one vintage in ``directory``, the way the hand-written ones were left in ``data/``."""
    payload = payload_of(rows)
    days = [day for day, _ in rows]
    entry = {
        "vendor": "yfinance",
        "symbol": "ZZZ",
        "price_basis": "adjusted",
        "first_date": min(days),
        "last_date": max(days),
        "path": name,
        "row_count": len(rows),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "download_date": "2026-02-01",
        "saved_date": None,
    }
    with open(directory / MANIFEST_NAME, "a", encoding="utf-8") as manifest:
        manifest.write(json.dumps(entry, sort_keys=True) + "\n")
    (directory / name).write_bytes(payload)


def halve_one_close(directory: Path, *, named: str, on: str) -> None:
    """Halve one close in a committed vintage's copy and repair its recorded hash.

    The span and the row count do not move, so the entry needs only its sha256
    rewritten. What this produces is two breaks rather than one: the day the
    close halves and the day it comes back.
    """
    path = directory / named
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines):
        if line.startswith(f"{on},"):
            day, close = line.split(",")[:2]
            lines[number] = f"{day},{float(close) / 2}"
            break
    else:
        raise AssertionError(f"{named} carries no row for {on}")
    payload = "".join(line + "\n" for line in lines).encode("utf-8")
    path.write_bytes(payload)
    rewrite_entry(directory, named, sha256=hashlib.sha256(payload).hexdigest())


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """An empty data directory with an empty manifest, never the committed one."""
    directory = tmp_path / "data"
    directory.mkdir()
    (directory / MANIFEST_NAME).write_text("", encoding="utf-8")
    return directory


@pytest.fixture
def committed_copy(tmp_path: Path) -> Path:
    """The committed vintages, copied, so a case may break one."""
    return copy_the_committed_tree(tmp_path)


@pytest.fixture
def halved(committed_copy: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """The committed tree with one GLD close halved, pointed at by the default.

    ``gld_20yr_prices_unadjusted.csv`` is the leg every entry point reads, so one
    edit reaches the replication and both figures. ``main`` takes no data
    directory, because it is a command line rather than a library call, so this
    moves the default the way ``tests/test_series.py`` does for the same reason.
    """
    halve_one_close(committed_copy, named="gld_20yr_prices_unadjusted.csv", on="2007-01-03")
    monkeypatch.setattr(paths, "DATA_DIR", committed_copy)
    return committed_copy


class TestTheMinuteFileIsReadAtItsDailyClose:
    def test_the_guard_reads_the_16_59_closes(self) -> None:
        """The guard reads one close a day, and it is the one Example 2.1 reads."""
        (entry,) = [
            entry
            for entry in read_manifest()
            if entry.path == "pythoncodesanddata/inputData_USDCAD.csv"
        ]

        assert closes_of(entry).equals(load_minute_close("USDCAD", dated=entry.saved_date)[1])


class TestTheGuardOverTheWholeManifest:
    """Rule 1. What the committed vintages carry, pinned as a count and as dates.

    The cost is not pinned with it, and not quoted either. A wall-clock figure
    is a property of the machine rather than of this code, which is why
    [issue 128](https://github.com/l3a0/quantitative-trading/issues/128)
    took the figures out of the docstrings. Neither is the
    number of passes over each series, since asserting one would mean counting
    operations or patching the parse, which is more machinery than the property
    is worth.
    """

    def test_the_whole_manifest_flags_exactly_the_pinned_days(self) -> None:
        found = breaks_across_the_manifest()

        assert found == EVERY_FLAG
        assert sum(len(days) for days in found.values()) == 300
        assert len(FLAGGED_IN_CHANS_MAT_FILES) == 96
        assert len(FLAGGED_IN_CHANS_FUTURES) == 7

    def test_every_committed_price_vintage_is_read_and_only_the_pinned_ones_report(self) -> None:
        """Said as its own case, because a guard that read one file would pass the count.

        The clean vintages are counted off the manifest rather than listed.
        Naming them would be the hand-written list this guard exists not to be,
        and it would fail on the day the next vintage lands whether or not that
        one changes scale. The claim here is that every price entry the
        manifest holds was read and answered, and that only the pinned ones
        answer with anything.
        """
        swept = {}
        for entry in price_entries():
            closes = closes_of(entry)
            swept[entry.path] = days_of(scale_breaks(closes))

        assert set(swept) == {entry.path for entry in price_entries()}
        assert {path: days for path, days in swept.items() if days} == EVERY_FLAG

    def test_only_vintages_that_hold_no_price_are_left_out(self) -> None:
        """The skip is by basis, so this says what it skips today: the bill series,
        Chan's 497 earnings flags, and the two rate files and the return file of
        his Python port."""
        skipped = {e.path for e in read_manifest()} - {e.path for e in price_entries()}
        assert {e.price_basis for e in read_manifest() if e.path in skipped} == {
            "rate",
            "event",
            "return",
        }
        assert {path for path in skipped if not path.startswith("earnannfile/")} == {
            "fred_tb3ms_rate_1934-01-01_2026-08-01_dl2026-09-30.csv",
            "pythoncodesanddata/AUD_interestRate.csv",
            "pythoncodesanddata/CAD_interestRate.csv",
            "pythoncodesanddata/AUDCAD_unequal_ret.csv",
        }
        assert len([path for path in skipped if path.startswith("earnannfile/")]) == 497

    def test_a_rate_series_would_report_breaks_if_it_were_read_as_a_price(self) -> None:
        """Why the skip exists, measured rather than asserted.

        Read as a price, the bill series clears the bound in 47 months at this
        vintage, most of them at rates under 1%. November 2015 is one: the rate
        went from 0.02% in October to 0.12%, six times over in a month, and
        nothing changed units.
        """
        (bills,) = [e for e in read_manifest() if e.symbol == "TB3MS"]
        flagged = days_of(scale_breaks(_parse_close(read_vintage(bills), bills.symbol)))
        assert len(flagged) == 47
        assert "2015-11-01" in flagged


class TestItSortsBeforeItDifferences:
    """Rule 2. The recorder writes rows in the order it is handed them, on purpose.

    ``_serialize``'s docstring says the file is meant to be what the vendor
    returned, so a vendor answering newest-first produces a vintage committed
    backwards. Differencing that reports every ratio inverted: a fully reversed
    ``ko_chan.csv`` still flags 2, because 0.5050 inverts to about 1.98 and that
    is over the bound too, so a count alone would not notice. The dates are what
    moves, and the dates are what these assert.
    """

    def test_a_series_handed_over_backwards_flags_the_day_the_scale_moved(self) -> None:
        forwards = scale_breaks(series_of(HALVES))
        backwards = scale_breaks(series_of(HALVES)[::-1])

        assert days_of(forwards) == ["2026-01-06"]
        assert days_of(backwards) == days_of(forwards)

    def test_a_shuffled_series_flags_the_same_day(self) -> None:
        """A reversal is one permutation. A guard sorting only the ends would pass it."""
        shuffled = series_of(HALVES).iloc[[2, 0, 3, 1]]

        assert days_of(scale_breaks(shuffled)) == ["2026-01-06"]

    def test_a_vintage_committed_backwards_reads_the_same_way_end_to_end(
        self, data_dir: Path
    ) -> None:
        """``_parse_close`` already sorts, so this pins the whole read rather than the guard."""
        rows = [(day, repr(close)) for day, close in zip(DAYS, HALVES, strict=True)]
        place(data_dir, name="backwards.csv", rows=list(reversed(rows)))

        _, closes = load_vintage("ZZZ", data_dir=data_dir)

        assert days_of(scale_breaks(closes)) == ["2026-01-06"]

    def test_the_two_known_breaks_are_recorded_rather_than_failing(self) -> None:
        """The guard's first run on `main` is red without this list, and the flags are real."""
        _, closes = load_vintage("KO", chan=True)

        assert days_of(scale_breaks(closes)) == KNOWN_BREAKS["ko_chan.csv"]


class TestANonFiniteRatioIsReportedNotSkipped:
    """Rule 3. "No break" and "could not tell" must not be the same answer.

    ``chan.vintage._unrecorded`` already writes that rule down for its own
    scan. Here it decides how the comparison is spelled. ``NaN > bound`` is
    ``False``, so a guard written that way reports a clean series over a close
    it could not read anything from, and numpy emits no warning saying so.
    """

    def test_a_nan_close_is_flagged_on_both_days_it_touches(self, data_dir: Path) -> None:
        """``_parse_close`` coerces an unparseable value to NaN.

        No committed vintage holds one, so the case writes its own.
        """
        place(
            data_dir,
            name="unreadable.csv",
            rows=[("2026-01-02", "100"), ("2026-01-05", "n/a"), ("2026-01-06", "52")],
        )

        _, closes = load_vintage("ZZZ", data_dir=data_dir)

        assert closes.isna().sum() == 1
        assert days_of(scale_breaks(closes)) == ["2026-01-05", "2026-01-06"]

    def test_a_negative_close_is_flagged_although_both_inputs_are_finite(self) -> None:
        """Its ratio's log is NaN out of two numbers ``_validated_rows`` would accept."""
        negative = series_of([10.0, -10.0, 11.0], days=DAYS[:3])

        assert days_of(scale_breaks(negative)) == ["2026-01-05", "2026-01-06"]

    def test_a_zero_close_is_flagged_and_warns_nobody(self) -> None:
        """``_validated_rows`` allows ``0.0``, which a vendor returns for a halted day.

        The ratios are ``0.0`` and ``inf``, both correctly flagged, and numpy
        raises a ``RuntimeWarning`` computing them. Turning warnings into
        errors here is what holds the suppression: without it this case fails
        rather than passing quietly.
        """
        halted = series_of([10.0, 0.0, 11.0], days=DAYS[:3])

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            flagged = scale_breaks(halted)

        assert days_of(flagged) == ["2026-01-05", "2026-01-06"]

    def test_a_series_too_short_to_difference_reports_nothing(self) -> None:
        """One row has no day-over-day move, which is not the same as an unreadable one."""
        assert scale_breaks(series_of([10.0], days=DAYS[:1])) == []
        assert scale_breaks(series_of([], days=[])) == []


class TestItIteratesTheManifest:
    """Rule 4. A new vintage is covered on the day it is recorded.

    ``COMMITTED`` in ``tests/test_series.py`` is a hand-written list somebody
    extends, and ``TestTheCommittedManifest`` iterates ``read_manifest()``
    instead. The guard follows the second, so this records a new vintage carrying a
    break and asks whether the scan found it. A hand-written list passes every
    other case in this file and fails this one.
    """

    @pytest.mark.parametrize("vendor", ["fred", "yfinance"])
    def test_a_recorded_rate_series_is_skipped_by_its_basis(
        self, committed_copy: Path, vendor: str
    ) -> None:
        """A second rate series is left out the day it is recorded, with no list to extend.

        Recorded under two vendors, because the basis is what decides and a skip
        keyed on the vendor that sent the first one would pass with ``fred`` alone.
        """
        record_vintage(
            list(zip(DAYS, HALVES, strict=True)),
            vendor=vendor,
            symbol="ZZZ",
            price_basis="rate",
            download_date="2026-09-18",
            data_dir=committed_copy,
        )

        assert breaks_across_the_manifest(committed_copy) == EVERY_FLAG

    @pytest.mark.parametrize("vendor", ["yfinance", "fred"])
    def test_a_new_recorded_vintage_carrying_a_break_is_found(
        self, committed_copy: Path, vendor: str
    ) -> None:
        """Found whichever vendor sent it, so a price from the vendor that sent the bill
        rate is still read for a break."""
        assert not [e for e in read_manifest(committed_copy) if e.symbol == "ZZZ"]
        entry = record_vintage(
            list(zip(DAYS, HALVES, strict=True)),
            vendor=vendor,
            symbol="ZZZ",
            price_basis="adjusted",
            download_date="2026-09-18",
            data_dir=committed_copy,
        )

        found = breaks_across_the_manifest(committed_copy)

        assert found == {**EVERY_FLAG, entry.path: ["2026-01-06"]}


class TestAWindowThatCrossesABreakStops:
    """Rule 5. Four windows, because a containment test against a flag list passes one.

    The guard run on the clipped series is the straddle test, so there is no
    flag table to match a window against. That matters in the third case below,
    where the flagged row is gone and the halving is still in the window, one
    day later. A precomputed list of flagged dates finds nothing there.
    """

    @pytest.fixture
    def ko(self) -> tuple[object, pd.Series]:
        return load_vintage("KO", chan=True)

    def test_a_window_straddling_a_break_refuses(self, ko) -> None:
        entry, closes = ko

        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(
                [(entry, closes)],
                start=pd.Timestamp("1965-02-01"),
                end=pd.Timestamp("1965-03-31"),
            )

        message = str(refused.value)
        assert "ko_chan.csv changes scale on 1965-02-19" in message
        assert "no readable day-over-day move" not in message
        assert "\n" not in message

    def test_a_window_starting_on_the_break_runs(self, ko) -> None:
        """The flagged date is the later of the two days, so a window opening there
        does not contain the move."""
        entry, closes = ko

        assert (
            refuse_window_crossing_a_break(
                [(entry, closes)],
                start=pd.Timestamp("1965-02-19"),
                end=pd.Timestamp("1965-03-31"),
            )
            is None
        )

    def test_a_window_whose_flagged_row_was_removed_still_refuses(self, ko) -> None:
        entry, closes = ko
        without = closes.drop(pd.Timestamp("1965-02-19"))

        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(
                [(entry, without)],
                start=pd.Timestamp("1965-02-01"),
                end=pd.Timestamp("1965-03-31"),
            )

        assert "1965-02-23" in str(refused.value)

    def test_the_default_ko_pep_window_runs(self) -> None:
        """Both KO breaks are in the 1960s and PEP starts in 1977, so nothing crosses one."""
        joined = aligned_closes("KO", "PEP", chan=True)

        assert str(joined.index[0].date()) == "1977-01-03"
        assert not joined.empty

    def test_the_check_reads_the_window_it_returns_and_not_the_one_it_was_asked_for(
        self,
    ) -> None:
        """The intersection with PEP is narrower than a 1962 start, and a check
        reading the argument would refuse a run that reads nothing wrong."""
        joined = aligned_closes("KO", "PEP", chan=True, start="1962-01-01")

        assert str(joined.index[0].date()) == "1977-01-03"

    def test_the_replication_reader_refuses_a_crossing_window(self, halved: Path) -> None:
        """The wiring, not the guard. ``aligned_closes`` is where the clip happens."""
        with pytest.raises(WindowCrossesScaleBreak) as refused:
            aligned_closes("GLD", "GDX", unadjusted=True, data_dir=halved)

        message = str(refused.value)
        assert "gld_20yr_prices_unadjusted.csv" in message
        assert "2007-01-03" in message

    def test_a_break_in_the_second_leg_refuses_too(self, committed_copy: Path) -> None:
        """The union across the legs, which every other case here reaches through leg A.

        The ``halved`` fixture breaks GLD, which is ``a`` in both
        ``aligned_closes`` calls this repo makes, so a guard reading only the
        first leg passed every other case in this file. Measured: truncating
        the loop to ``list(legs)[:1]`` left the whole suite green.
        """
        halve_one_close(committed_copy, named="gdx_20yr_prices_unadjusted.csv", on="2007-01-03")

        with pytest.raises(WindowCrossesScaleBreak) as refused:
            aligned_closes("GLD", "GDX", unadjusted=True, data_dir=committed_copy)

        assert "gdx_20yr_prices_unadjusted.csv changes scale" in str(refused.value)

    def test_an_unreadable_close_is_named_as_unreadable_rather_than_as_a_break(
        self, data_dir: Path
    ) -> None:
        """Two states, two sentences. A NaN close is not a series that changed scale.

        The refusal still fires, because the guard cannot rule a break out
        across a day it could not read and "no break" and "could not tell" must
        not be the same answer. What it may not do is report the wrong one of
        the two, which is the rule ``tests/test_series.py`` states for the four
        refusals already there. This is reachable through a run whose own frame
        drops the row, since ``aligned_closes`` ends in a ``dropna``.
        """
        place(
            data_dir,
            name="unreadable.csv",
            rows=[("2026-01-02", "100"), ("2026-01-05", "n/a"), ("2026-01-06", "52")],
        )
        entry, closes = load_vintage("ZZZ", data_dir=data_dir)

        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(
                [(entry, closes)], start=closes.index[0], end=closes.index[-1]
            )

        message = str(refused.value)
        assert "unreadable.csv has no readable day-over-day move on" in message
        assert "2026-01-05, 2026-01-06" in message
        assert "changes scale" not in message

    def test_a_window_the_two_legs_do_not_share_is_not_an_error(self) -> None:
        """An empty intersection has no first day to hand the check, and is not a refusal.

        Measured: without the emptiness branch at the call site,
        ``joined.index[0]`` raises ``IndexError`` through a public call.
        """
        joined = aligned_closes("KO", "PEP", chan=True, start="2030-01-01", end="2030-12-31")

        assert joined.empty

    def test_a_window_clear_of_the_halving_still_runs(self, halved: Path) -> None:
        """A refusal that fired on the whole vintage rather than the window passes
        the case above and fails this one."""
        joined = aligned_closes("GLD", "GDX", unadjusted=True, start="2011-01-03", data_dir=halved)

        assert not joined.empty


class TestTheRefusalIsAType:
    """Rule 6. Caught by every ``main`` that reads the pair, and told apart from the other refusal.

    A vintage being unavailable and a window crossing a break are two problems
    with two fixes. ``chan.vintage`` already argues that sharing an exception
    hands the next reader a docstring describing something that did not happen,
    and that argument is why ``VintageRefused`` sits beside ``VintageUnavailable``.
    """

    def test_it_is_not_a_kind_of_vintage_unavailable(self) -> None:
        assert not issubclass(WindowCrossesScaleBreak, VintageUnavailable)
        assert not issubclass(VintageUnavailable, WindowCrossesScaleBreak)

    def test_the_replication_command_prints_a_line(
        self, halved: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from chan import pair_cointegration

        monkeypatch.setattr(sys, "argv", ["chan.pair_cointegration", "--ch7"])
        with pytest.raises(SystemExit) as stopped:
            pair_cointegration.main()

        message = str(stopped.value)
        assert "gld_20yr_prices_unadjusted.csv" in message
        assert "2007-01-03" in message
        assert "\n" not in message

    def test_the_figure_command_prints_a_line(
        self, halved: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """``main`` takes no output path, so the figure directory is moved instead.

        Without that, a run reaching ``savefig`` writes over the committed
        ``docs/figures/reproduction_regime_map.png``, which is a tracked
        artifact three surfaces are held to. The refusal is what stops it
        today, and a test whose own correctness depends on the thing it is
        testing overwrites the figure the moment it regresses. Measured:
        deleting the call in ``aligned_closes`` left the committed PNG modified
        in the working tree.
        """
        from chan import regime_figure

        monkeypatch.setattr(regime_figure, "FIGURES_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            regime_figure.main()

        message = str(stopped.value)
        assert "gld_20yr_prices_unadjusted.csv" in message
        assert "2007-01-03" in message
        assert "\n" not in message

    def test_the_residual_figure_command_prints_a_line(
        self, halved: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The halved day, 2007-01-03, sits inside the Chapter 3 window this
        figure reads, so the refusal reaches it as well."""
        from chan import lag_residual_figure

        monkeypatch.setattr(lag_residual_figure, "FIGURES_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            lag_residual_figure.main()

        message = str(stopped.value)
        assert "gld_20yr_prices_unadjusted.csv" in message
        assert "2007-01-03" in message
        assert "\n" not in message


class TestTheBoundIsTheOneThatWasMeasured:
    """The envelope the single-series vintages actually span, run rather than quoted.

    The bound is computed from 1.6 rather than typed as 0.4700, because a price
    ratio is multiplicative and ``[0.6, 1.6]`` is asymmetric by 0.0408 in log
    terms. A guard built on a pair of endpoints answers differently on a series
    and on the same series reversed, which is the property the first case here
    holds.
    """

    def test_it_is_the_log_of_one_point_six(self) -> None:
        assert SCALE_BREAK_BOUND == math.log(1.6)

    def test_a_move_and_its_reciprocal_are_judged_the_same(self) -> None:
        """0.62 and 1.613 straddle ``[0.6, 1.6]`` and sit the same side of this bound."""
        rising = series_of([10.0, 16.13], days=DAYS[:2])
        falling = series_of([16.13, 10.0], days=DAYS[:2])

        assert days_of(scale_breaks(rising)) == ["2026-01-05"]
        assert days_of(scale_breaks(falling)) == ["2026-01-05"]

    def test_black_monday_is_not_a_scale_break(self) -> None:
        """The widest legitimate move in a stock or fund vintage, at 0.7521.

        It is in ``ko_chan.csv``. It was the widest in the whole envelope until
        the EIA futures vintages landed. Several futures days now sit outside
        it, and the margin test below pins the widest fall and the widest rise
        among them. That test also says why the stocks lifted from Chan's MATLAB
        files are not held to the envelope.
        """
        _, closes = load_vintage("KO", chan=True)

        assert "1987-10-19" not in days_of(scale_breaks(closes))

    def test_the_siblings_band_would_miss_both_ko_breaks(self) -> None:
        """``[0.5, 2.0]`` is deliberately not ported. It runs on already-adjusted
        closes next door, where a correct split leaves no cliff at all, and both
        breaks here sit inside it at 0.5050 and 0.5047."""
        _, closes = load_vintage("KO", chan=True)

        assert scale_breaks(closes, bound=math.log(2.0)) == []

    def test_the_committed_ratios_leave_a_margin_on_both_sides(self) -> None:
        """What carries forward to the next vintage is this derivation, not the number.

        Every number the prose quotes about the envelope is derived here, which
        is the single-authority rule. ``docs/design.md``'s register and
        ``chan.series``'s own docstring state these and never recompute them.
        One of them is corrected against the issue that specified it: the
        smaller break is 0.68329 and rounds to 0.6833, where
        [issue 3](https://github.com/l3a0/quantitative-trading/issues/3) prints
        the truncation 0.6832.

        It reads the single-series vintages the bound was fitted to and skips
        every column lifted from one of Chan's files, whose flags
        ``FLAGGED_IN_CHANS_MAT_FILES`` and ``FLAGGED_IN_CHANS_FUTURES`` pin
        instead. Holding them to an envelope
        fitted to the single-series vintages, mostly funds, indexes and
        futures, would assert that a small cap never moves 40 percent in a day.
        Chan's futures strips and continuous futures saves are skipped with
        them, although they are futures, and so is his ``VIX.csv``, although it
        is not a MATLAB file, because the skip is by source rather than by asset.
        ``tests/test_futures_strips.py`` pins their widest move on its own, and
        it would widen this envelope's lower end.

        The twelve EIA futures vintages moved both ends of the envelope. The
        widest fall is now 0.6810, RBOB gasoline's first contract on
        2020-03-23, and the widest rise is 1.4648, natural gas's first contract
        on 2022-01-27. Without them the two ends are Black Monday's 0.7521 in
        ``ko_chan.csv`` and 1.2654, and the widest magnitude is 0.2849, which
        the case pins too so the stock and fund envelope stays derived. The
        range also holds days on which a futures file's contract rolled, which
        compare two contracts rather than one price, so it is a range of what
        the bound must let through rather than of price moves alone.

        Moving the envelope moved which other bounds would serve, and the last
        assertions pin the example ``chan.series`` gives.
        """
        widest, breaks, ratios, kept, kept_without_futures = 0.0, [], [], [], []
        for entry in price_entries():
            if in_a_lifted_source(entry.path):
                continue
            closes = closes_of(entry)
            values = closes.to_numpy(dtype=float)
            moves = values[1:] / values[:-1]
            magnitudes = np.abs(np.log(moves))
            flagged = magnitudes > SCALE_BREAK_BOUND
            widest = max(widest, float(magnitudes[~flagged].max()))
            breaks.extend(magnitudes[flagged])
            ratios.extend(moves[flagged])
            kept.extend(moves[~flagged])
            if entry.vendor != "eia":
                kept_without_futures.extend(moves[~flagged])

        assert round(widest, 4) == 0.3842
        assert (round(min(kept), 4), round(max(kept), 4)) == (0.6810, 1.4648)
        assert [round(float(one), 4) for one in sorted(breaks)] == [0.6833, 0.6838]
        assert sorted(round(float(one), 4) for one in ratios) == [0.5047, 0.5050]
        assert widest < SCALE_BREAK_BOUND < min(breaks)

        stocks_and_funds = (min(kept_without_futures), max(kept_without_futures))
        assert tuple(round(one, 4) for one in stocks_and_funds) == (0.7521, 1.2654)
        assert round(max(abs(math.log(one)) for one in stocks_and_funds), 4) == 0.2849

        assert widest < math.log(1.5) and math.log(1.9) < min(breaks)
        assert math.log(1.45) < widest

    def test_a_band_of_endpoints_would_judge_the_same_move_two_ways(self) -> None:
        """The 0.0408 the register quotes, derived rather than restated.

        ``[0.6, 1.6]`` is the band the bound would have been written as. Its two
        endpoints are that far apart in log terms, which is the whole of why the
        bound is on the log instead."""
        assert round(abs(math.log(0.6)) - abs(math.log(1.6)), 4) == 0.0408


class TestWhyTheComparisonDetectorWasCut:
    """The rejected detector's decisive number, pinned so the design doc can quote it.

    Comparing a symbol's raw vintage against its adjusted one was the other
    candidate for noticing a split. A split rescales both bases together, so
    dividing one by the other cancels exactly the thing being looked for, and
    what is left is dividend drift. ``docs/design.md``'s register carries the
    reasoning and this carries the number, because a cheap check nobody wrote
    down gets re-derived from scratch and the same dead end costs the same
    afternoon twice.
    """

    def test_dividing_gdx_adjusted_by_gdx_raw_moves_too_little_to_detect_anything(
        self,
    ) -> None:
        both = adjusted_against_raw("GDX")
        ratio = both.adjusted / both.raw
        widest = float(ratio.diff().abs().max())

        assert round(widest, 4) == 0.0163
        assert widest < 1 - math.exp(-SCALE_BREAK_BOUND)


class TestWhichColumnTheHandPlacedAdjustedVintagesHold:
    """GLD's and GDX's calls were never written down, so their bytes answer instead.

    Both adjusted files were downloaded before anything here recorded a call,
    so the `vendor_column` their lines carry was typed from this comparison
    rather than from a call. Each has a raw twin from the same vendor, which is
    yfinance's split-only `Close`. A close carrying the dividends sits below
    that twin on every day before the last ex-dividend date in the file and
    equals it from that date on, because the adjustment is a factor applied
    backwards from each payment. A split-only close mislabelled as adjusted
    equals its twin everywhere instead.

    That last sentence is also true of a fund that pays nothing, which is GLD.
    So GLD's comparison cannot say which column it holds, and says instead that
    the two columns are one series for this file and the route cannot move a
    number read from it.

    The pair is loaded through `adjusted_against_raw`, which is what
    `TestWhyTheComparisonDetectorWasCut` above reads, so the two cannot come to
    compare different series. It sits here rather than in
    `tests/test_vintage.py` because that file tests `chan.vintage`, which keeps
    to the standard library so its tests do not import pandas, and this reads
    series.
    """

    def test_gld_s_adjusted_vintage_equals_its_raw_twin_on_every_shared_day(self):
        both = adjusted_against_raw("GLD")

        assert len(both) == 5030
        assert (both.adjusted == both.raw).all()

    def test_gdx_s_sits_below_its_raw_twin_before_its_last_ex_date_and_equals_it_after(self):
        both = adjusted_against_raw("GDX")
        last_ex_date = pd.Timestamp("2025-12-22")
        before = both[both.index < last_ex_date]
        after = both[both.index >= last_ex_date]

        assert len(both) == 5099
        assert (before.adjusted < before.raw).all()
        assert (after.adjusted == after.raw).all()
        assert (len(before), len(after)) == (4928, 171)


class TestIWBsAdjustedVintageCarriesTheDividends:
    """IWB's adjusted line records its call, and its raw twin checks the label against bytes.

    Both files came from one session on 2026-10-03, the adjusted one from
    ``Close`` under ``auto_adjust=True`` and the twin from ``Close`` under
    ``auto_adjust=False``, which carries splits and not dividends.
    [Issue 160](https://github.com/l3a0/quantitative-trading/issues/160)
    recorded the twin for this comparison. A split-only close recorded as
    ``adjusted`` would strip IWB's dividends, and the risk parity run would
    then report the missing dividends as what the SPY proxy cost.

    The comparison takes the shape GDX's above does. The adjusted close sits
    below the twin on every day before the last ex-dividend date in the file
    and equals it from that date on, because the adjustment is a factor applied
    backwards from each payment. The ratio of the two moves only on the days a
    payment goes ex, so the count of its steps is a count of distributions.
    """

    def test_it_sits_below_its_raw_twin_before_its_last_ex_date_and_equals_it_after(self):
        both = adjusted_against_raw("IWB")
        last_ex_date = pd.Timestamp("2026-09-15")
        before = both[both.index < last_ex_date]
        after = both[both.index >= last_ex_date]

        assert len(both) == 6632
        assert (before.adjusted < before.raw).all()
        assert (after.adjusted == after.raw).all()
        assert (len(before), len(after)) == (6618, 14)

    def test_the_ratio_steps_once_per_distribution_and_only_upward(self):
        """108 steps of at least 0.05 percent, against stored-float noise under 1e-6.

        Each close is stored at its shortest round-trip repr, so the ratio of two
        of them wobbles in the seventh decimal on days nothing happened. A step
        clears that by more than two orders of magnitude, so the threshold
        between them is not a judgement call. Every step raises the ratio toward
        1, which is a payment's factor coming off, and the last is the last
        ex-date above. About four a year over 26 years is a quarterly payer.
        """
        both = adjusted_against_raw("IWB")
        moves = (both.adjusted / both.raw).diff().dropna()
        steps = moves[moves.abs() > 1e-5]
        noise = moves[moves.abs() <= 1e-5]

        assert len(steps) == 108
        assert (steps > 0).all()
        assert steps.abs().min() > 5e-4
        assert noise.abs().max() < 1e-6
        assert steps.index[-1] == pd.Timestamp("2026-09-15")
