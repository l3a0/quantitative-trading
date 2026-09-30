# The Kelly leverage on SPY depends on which years are read

*Reproducing Chan’s Example 6.2 on a 2026 download: the formula holds, every level moves, and the window moves the answer most.*

## Why one leverage figure is not enough

Ernest Chan’s *Quantitative Trading* (Chan, 2021) works the Kelly formula on SPY, the exchange-traded fund that tracks the S&P 500, in Example 6.2 of Chapter 6. Over SPY’s history from January 1993 to the end of 2007, he finds that the leverage that makes capital grow fastest is 2.528 times equity. A trader with \$100,000 would hold \$252,800 of SPY.

Reading the same fund over the same dates from a 2026 download gives 2.551. Reading only 2000 to 2002 gives −2.82, which is a short. Reading only 2003 to 2007 gives 4.90. The formula is exact, and each of those numbers is correct for its inputs. What moves the answer is the inputs, and the choice of years moves it most.

This post walks through the formula and six lessons from reproducing Chan’s example in code. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The Kelly formula

Kelly sizing comes from John Kelly’s work on betting (Kelly, 1956), which asked what share of capital to stake so that wealth grows fastest over many rounds. Chan uses its continuous form, which reads the leverage straight off a return series’ mean and standard deviation:

```math
f^* = \frac{m}{s^2}
```

Here `m` is the mean annual **excess return**, the return above a risk-free rate, and `s` is the annual standard deviation. Chan sets the risk-free rate `r` at 4%. **Leverage** is the position divided by equity, so a leverage of 2 means \$2 of SPY for every \$1 of the trader’s own money, with the rest borrowed.

At that leverage capital compounds at the fastest possible rate. Chan gives the rate in terms of the **Sharpe ratio** `S = m/s`, the excess return per unit of risk:

```math
g^* = r + \frac{S^2}{2}
```

Without leverage, the account compounds at the mean return less half the variance, a cost called volatility drag:

```math
g = r + m - \frac{s^2}{2}
```

Here are Chan’s figures beside the ones this repo computes on the same window:

```math
\begin{array}{l|r|r}
\text{Quantity} & \text{Chan (2021)} & \text{2026 download} \\ \hline
\text{Mean annual return} & 11.23\% & 11.29\% \\
\text{Standard deviation} & 16.91\% & 16.91\% \\
\text{Mean excess return} & 7.231\% & 7.295\% \\
\text{Sharpe ratio} & 0.4275 & 0.4313 \\
\text{Kelly leverage} & 2.528 & 2.551 \\
\text{Growth at full Kelly} & 13.14\% & 13.30\% \\
\text{Growth without leverage} & 9.8\% & 9.9\% \\
\text{Half-Kelly leverage} & 1.26 & 1.28
\end{array}
```

On this window, levering to the Kelly figure raises the growth rate from about 9.9% a year to 13.3%.

## Lesson 1: every level moved and no claim did

Every level computed from the series lands slightly above Chan’s. The mean is 0.06 percentage points higher, the Sharpe ratio 0.0038 higher and the leverage 0.023 higher. Every claim those numbers support still holds. SPY returned about 11% a year over his span, the growth-maximising leverage is about two and a half, and levering to it lifts growth above the unlevered rate.

The cause is the data vendor rather than the method. Chan read an **adjusted close**, a price series rewritten so that dividends and splits do not show up as jumps in price. Each new dividend rescales the whole history behind it, so an adjusted series downloaded in 2008 and one downloaded in 2026 disagree about the same day. This repo calls each download a **vintage** and keeps the file, because a number computed from a series nobody kept is a number nobody can check.

The one figure that reproduces exactly is the standard deviation, at 16.91%. Restatement moves where a series sits far more than how much it moves, so the mean drifted and the spread did not.

A published number is therefore a snapshot of one download, and the claim it supports is the part that lasts. A backtest that quotes a figure without naming its data vintage quotes something nobody can check, its author included.

## Lesson 2: the formula hides two choices, and each wrong answer looks right

Chan prints results rather than code, but his own MATLAB for the next example, `example6_3.m`, settles how he computed them. Two of those choices are easy to get wrong without noticing.

1. **Which standard deviation.** A standard deviation can divide by the number of returns `n`, the population form, or by `n − 1`, the sample form. His code uses MATLAB’s `cov`, which takes the sample form. On this download the two forms differ by 5.74e-5 on the Sharpe ratio and 6.79e-4 on the leverage. At the three decimals Chan gives the leverage, both forms print the same number, so a check on the leverage alone cannot tell them apart. Only the Sharpe ratio, printed to four decimals, can.
2. **What `m` means.** Chan’s formulas use the excess return, but the sentence beside his unlevered growth rate calls `m` “the annualized mean return”. Following that wording adds the whole risk-free rate back and turns 9.86% into 13.86%. A four-point error reads as a problem with the data rather than a misread symbol.

Both wrong answers produce numbers that look reasonable, which is what makes them dangerous. A reported Sharpe ratio or Kelly leverage should say which standard deviation it used and whether its return is total or excess.

## Lesson 3: a constant leverage sells into a loss

Chan’s worked example follows the leverage through a bad day. With \$100,000 of equity at 2.528, the account holds \$252,800 of SPY and owes \$152,800. SPY then falls 10%, so the position is worth \$227,520 and equity is down to \$74,720. The loss on equity is 2.528 times the fund’s fall.

To get back to 2.528 times equity, the account has to shrink the position to \$188,892, selling SPY straight after it fell. Every figure in that chain is arithmetic on Chan’s rounded 2.528, so it reproduces to the cent.

The same arithmetic runs the other way after a gain, when the rule buys. An account held at a constant leverage sells after losses and buys after gains, which is the behaviour of a momentum trader, whatever the strategy underneath.

## Lesson 4: the stress test has a threshold, and it sits close

Chan then asks whether the Kelly leverage would have survived Black Monday, 19 October 1987, when the S&P 500 fell 20.47% in a day. If a trader can tolerate losing 20% of equity in one day, the leverage that allows is 0.20 divided by 0.2047, which is 0.977 and which Chan calls “about 1”. **Half-Kelly**, trading at half the Kelly leverage to cut risk, is 1.26 in his figures. Since 1.26 is above 0.977, he concludes that even half-Kelly would not have survived that day. At full Kelly on this download, a repeat of that day would cost 52.21% of equity.

The conclusion holds while half the Kelly leverage exceeds 0.977, which means while the full leverage exceeds 1.954. This download gives 2.551, a margin of 0.60. On Chan’s own spreadsheet, reading the as-traded close instead of the adjusted close gives a leverage of 1.93, which is below the line. The choice of price series alone reverses his conclusion.

The 20.47% needs two cautions.

1. SPY started trading in January 1993, so no SPY data can check a figure from 1987. It belongs to the index, and this replication takes it as Chan’s constant.
2. The worst day SPY itself holds in Chan’s window is a 7.25% fall on 27 October 1997, about a third of Black Monday. Through September 2026 its worst is 10.94%, on 16 March 2020.

Setting half-Kelly’s 1.28 against an allowed 0.977 makes the conclusion look comfortable. The threshold shows that the full leverage has 0.60 to spare, and that one data choice can spend it.

## Lesson 5: the window moves the answer further than the vendor does

The same download and the same formula give very different leverages on different years.

1. 1993 to 2007, Chan’s window: 2.551.
2. 2000 to 2002, the dot-com bear market: −2.82. The mean excess return was negative, so Kelly recommends a short of 2.82 times equity.
3. 2003 to 2007, the bull market that followed: 4.90.
4. 1993 to September 2026, the whole download: 2.33.

The vendor moved the leverage by 0.023. The choice of years moves it by 7.72, from a short to nearly five times long.

The longest window shows what stays put. Nineteen more years lowered the leverage from 2.551 to 2.33 and left the Sharpe ratio at 0.4315, against 0.4313 on Chan’s span. The leverage is also `S/s`, so a steady Sharpe ratio and a standard deviation that rose to 18.53% give a smaller leverage.

The reason is in the formula. The variance `s²` on Chan’s window is about 0.03, so dividing by it multiplies any error in the mean by about 35. A mean estimated from three or five years swings widely, and the leverage swings with it.

A negative leverage needs care. Half of −2.82 is a smaller short rather than a safer position, and Chan’s stress test measures a long position’s worst day, so neither carries across the change of sign.

## Lesson 6: the leverage depends on how often returns are measured

Chan notes that the Kelly leverage, unlike the Sharpe ratio, does not depend on the time scale. In one reading that is an identity. Annualising multiplies the mean by 252 and the variance by 252, so the factor cancels and daily and annual moments give the same leverage. Testing that says nothing about SPY.

The reading that matters is whether monthly returns give the same answer as daily ones, and they do not. Monthly has three reasonable definitions.

1. Month-end closes give 3.72.
2. Month-end closes with the unfinished last month dropped give 3.75.
3. Blocks of 21 trading days give 3.64.

All three sit near 3.7, against 2.551 from daily returns, which is 43 to 47 percent higher. Which monthly definition is picked barely matters, while monthly against daily matters a great deal. Why SPY’s monthly returns imply a larger leverage is outside what this replication tests. What it shows is that the return frequency is a choice, and a reported Kelly leverage should name it along with the window.

## What this means for a trader

The replication reproduces Chan’s figures on one download of one fund. It is exploratory. It can say that his claims survive and why his numbers moved, and it says nothing about whether leverage of this size is a good idea today. A leverage computed from one sample is a reference point rather than a recommendation.

Four habits follow from the lessons above.

1. **Name the window.** It moved the leverage more than anything else here.
2. **Name the specification.** Say which standard deviation, whether the return is total or excess, which price series and which return frequency.
3. **Find the threshold.** Compute where a risk conclusion turns over, rather than setting two numbers side by side.
4. **Treat full Kelly as a ceiling.** The formula gives the fastest growth only when the mean and the standard deviation are known, and a sample only estimates them.

Chan’s claims survive eighteen years of restated data. SPY’s growth-maximising leverage over his window is about two and a half, and even half of it would not have survived a repeat of Black Monday. What a trader should carry away is the range around his 2.528, from a short of 2.82 to a long of 4.90, set by nothing but the years read.

## References

- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley.
- Kelly, J. L. (1956). A new interpretation of information rate. *Bell System Technical Journal*, 35(4), 917–926.

*Not investment advice. Code: [the Kelly calculation](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/kelly_leverage.py), with the checks behind [every number](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_kelly_leverage.py) and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-3-kelly-leverage-on-spy-chans-quantitative-trading) that sets each of Chan’s figures beside the one reproduced here.*
