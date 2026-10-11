# Under a cap of 2, Chan’s fastest-growing Kelly allocation holds one strategy, and every figure he prints reproduces

*Chapter 8 of Algorithmic Trading shows that shrinking every Kelly leverage to fit a broker’s cap is not the allocation that grows fastest. Every printed figure lands, his 0.96 is a tie rounded up, and on his inputs the answer changes once the cap passes 2.45.*

## Why a leverage cap changes the answer

The Kelly formula says how much leverage makes capital grow fastest. Ernest Chan’s second book, *Algorithmic Trading*, treats that number as a ceiling. His experience is that the Kelly leverage “is best viewed as an upper bound”, and that it often comes out so high “that it far exceeds the maximum leverage allowed by our brokers” (Chan, 2013, location 3235). So the question a trader with several strategies faces is how to spend the leverage a broker allows, rather than how to reach Kelly.

Chan answers it with Example 8.2, two strategies under a broker’s cap of 2. The usual advice shrinks every Kelly leverage by one factor until the total fits. His example shows that putting the whole cap on the better strategy grows faster. Example 8.1, just before it, shows what holding a leverage constant asks of a trader after a loss and after a gain.

This repository reproduced both examples in code. The results fall into three groups.

1. **Every figure the book prints lands.** The trades of Example 8.1 match to the dollar, and the leverages and growth rates of Example 8.2 match at the precision Chan prints them.
2. **Shrinking every leverage loses to putting everything on one strategy.** Both leverages shrunk to the cap grow at 0.816798. The whole cap on strategy 2 grows at 0.955.
3. **The book’s 0.96 is a tie rounded up.** The exact growth rate with everything on strategy 2 is 0.955, halfway between 0.95 and 0.96, and the usual way to print a number at two decimals in code gives 0.95.

**These results are neither exploratory nor registered.** A result is exploratory when a sample of data was spent looking for it, and registered when its hypothesis was written down before any number was seen. Both examples are arithmetic on inputs the book states, so no sample was spent. They say nothing about a real pair of strategies.

The six lessons below say what the reproduction teaches. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## Two strategies and a cap of 2

Example 8.2’s two strategies have annual mean excess returns of 30 and 60 percent, meaning returns above the risk-free rate, and annual volatilities of 26 and 35 percent. Their returns are uncorrelated, the risk-free rate is 0 and the broker allows a leverage of 2 (Chan, 2013, location 3287).

The cap is on **gross leverage**. Location 3268 defines it as “the absolute sum of the long and short market values divided by our equity”. A trader with \$1 of equity, \$1.50 long in one strategy and \$0.50 short in another, has a gross leverage of 2 and a net leverage, long less short, of 1. Because the cap is on the gross, a short uses it up as much as a long does.

The [post on the Kelly leverage on SPY](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md) derives the one-strategy formula from Chan’s first book. With a mean excess return m and a standard deviation s, the leverage that grows fastest is m / s², and the growth rate there is r + S² / 2, where r is the risk-free rate and S = m / s is the Sharpe ratio.

With several strategies the leverage becomes a vector, one leverage per strategy drawn from a common pool of equity. Chan writes it as F, and location 3259 says the Kelly formula “tells us how to optimally allocate our buying power”:

```math
F = C^{-1} M
```

M holds each strategy’s mean excess return and C is the covariance matrix of their returns. When the strategies are uncorrelated, C has only the variances on its diagonal, and each leverage reduces to the one-strategy m / s². Strategy 1 gets 4.437870 and strategy 2 gets 4.897959, for a gross total of 9.335829. Chan prints 4.4, 4.9 and 9.3.

Chan cites Thorp (1997) for Equation 8.3, the growth rate at the Kelly leverages, and adds that it “applies only when the leverages used are optimal” (Chan, 2013, location 3287). At any leverages F, the growth rate is

```math
g = r + F'M - \frac{F'CF}{2}
```

Here r is 0, as the example assumes, and F′ is F laid on its side, so each product sums over the strategies. The [post on the coin toss](https://github.com/l3a0/quantitative-trading/blob/main/blog/coin-toss-expected-value-vs-growth.md#lesson-3-variance-is-a-cost-charged-against-growth) shows why compound growth falls short of the average return by about half the variance. So the formula reads as two terms.

1. **The return**, F′M, what the leverages earn on average.
2. **The drag**, F′CF / 2, half the variance of the levered portfolio, which compounding takes back.

The growth rate is the return less the drag. With one strategy, the formula gives the SPY post’s r + S² / 2 at the Kelly leverage. With two uncorrelated strategies it gives half the sum of their squared Sharpe ratios, which are 1.153846 and 1.714286, so the uncapped Kelly leverages grow at 2.135068 a year. Their return is 4.270136 and their drag 2.135068, exactly half of it, the same split the SPY post finds for one strategy.

Chan gives this growth rate as Equation 8.3, an image the highlights this repository works from did not capture. So 2.135068 is quoted as computed, with no published figure beside it.

## Lesson 1: every figure the book prints lands, and nothing about the data could have moved them

Here is each figure Chan prints for the two examples, computed beside printed.

```math
\begin{array}{l|r|r}
\text{Figure} & \text{Computed} & \text{Book} \\ \hline
\text{8.1, position after the 10K loss, dollars} & 490{,}000 & 490\text{K} \\
\text{8.1, trade back to leverage 5, dollars} & -40{,}000 & \text{sell } 40\text{K} \\
\text{8.1, position after the 20K gain, dollars} & 470{,}000 & 470\text{K} \\
\text{8.1, trade back to leverage 5, dollars} & +80{,}000 & \text{buy } 80\text{K} \\
\text{8.2, Kelly leverage, strategy 1} & 4.437870 & 4.4 \\
\text{8.2, Kelly leverage, strategy 2} & 4.897959 & 4.9 \\
\text{8.2, total gross Kelly leverage} & 9.335829 & 9.3 \\
\text{8.2, leverages scaled to the cap} & 0.950718,\ 1.049282 & 0.95,\ 1.05 \\
\text{8.2, growth rate at those leverages} & 0.816798 & 0.82 \\
\text{8.2, growth rate, everything on strategy 2} & 0.955 & 0.96
\end{array}
```

Each figure lands, meaning it matches the book at the precision the book prints. The last needs Lesson 3 to explain how 0.955 prints as 0.96.

Example 8.1 holds a leverage of 5 on \$100,000 of equity, a \$500,000 position. A \$10,000 loss leaves \$90,000 of equity and a \$490,000 position, so getting back to 5 means selling \$40,000, which leaves a \$450,000 position. A \$20,000 gain the next day leaves \$110,000 of equity and a \$470,000 position, and getting back to 5 means buying \$80,000. Chan concedes the discomfort in the example itself: “This selling into the loss may make some people uncomfortable” (Chan, 2013, location 3216). Location 3210 explains why he asks for it anyway. However the leverage was chosen, “the leverage should be kept constant”. The SPY post’s [Lesson 3](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md#lesson-3-a-constant-leverage-sells-into-a-loss) works the same mechanism on SPY. A leverage held constant above 1 sells after every loss and buys after every gain, and Example 8.1’s trades run through the same function as the SPY post’s.

Location 3228 adds why the selling matters beyond one account. When many funds hold similar positions, one fund’s forced sales cause losses for the others, whose own sales deepen them, “a vicious cycle”. Chan notes that analysts cited this as a cause of the August 2007 meltdown of quantitative funds (Khandani and Lo, 2007). The [post on Chan’s rerun of the Khandani-Lo reversal](https://github.com/l3a0/quantitative-trading/blob/main/blog/khandani-lo-reversal-lessons.md) reproduces the trading rule from that paper.

No choice of data could have moved these figures. Nothing between the stated inputs and the result depends on a data vendor, a download date or a window, so every verdict was known before the code was written. What the reproduction adds is three things the table does not show.

1. The exact value behind the printed 0.96, in Lesson 3.
2. The near miss, in Lesson 4.
3. Where everything on strategy 2 stops being best, in Lesson 5.

## Lesson 2: scaling every leverage down is the recommendation the example refutes

Location 3268 states the advice the example refutes: “The usual recommendation is to multiply all Fi” by the cap over the total, so the gross leverage equals the cap. Here that factor is 0.214228, and the scaled leverages are 0.950718 and 1.049282, the book’s 0.95 and 1.05. This post calls that the **proportional split**. It grows at 0.816798.

Chan then fixes the gross at the cap, sets F1 = 2 − F2 and draws the growth rate as F2 runs from 0 to 2. His Figure 8.1 is that curve, captioned “Constrained Growth Rate g as Function of F2” (Chan, 2013, location 3287). Along that line the slope of the growth rate is

```math
\frac{dg}{dF_2} = 0.4352 - 0.1901\,F_2
```

At F2 = 0, with everything on strategy 1, the slope is 0.4352. That is how fast the growth rate rises as leverage moves from strategy 1 to strategy 2, and it is positive because strategy 2 earns more and strategy 1 sheds drag. Each unit of leverage moved lowers the slope by 0.1901, the two variances added together. At F2 = 2 the slope is still 0.0550, above zero, so the growth rate rises over the whole range. It peaks at F2 = 2 with F1 = 0, everything on strategy 2. This post calls that allocation the **corner**, since it sits at the end of the allowed range.

![A curve of the growth rate g against F2, the leverage on strategy 2, with F1 = 2 − F2 on strategy 1, for F2 from 0 to 2.6. A solid curve rises from 0.4648 at F2 = 0, with everything on strategy 1, to 0.955 at F2 = 2, with everything on strategy 2. A filled brown marker sits on it at the proportional split, F2 = 1.049282 and g = 0.816798, and a filled green marker at the corner, F2 = 2 and g = 0.955. Past F2 = 2 the curve continues dashed over a shaded region labelled as over the gross cap of 2, where strategy 1 is held short. The dashed curve rises a little further to a hollow red marker at the unbounded peak, F2 = 2.289321 and g = 0.962956, labelled as not allowed, and falls slightly toward F2 = 2.6.](../docs/figures/kelly_allocation.png)

*The growth rate along the line where the whole cap of 2 is spent. The solid curve from F2 = 0 to 2 redraws the book’s Figure 8.1, “Constrained Growth Rate g as Function of F2”. The dashed part past the cap, the shading and the three markers are added here, and the book does not draw them.*

The corner beats the proportional split by 0.138202, and grows 1.169199 times as fast. Splitting the two growth rates into return and drag says why.

1. **The proportional split** earns a return of 0.914785 and pays a drag of 0.097986.
2. **The corner** earns a return of 1.2 and pays a drag of 0.245.

So the proportional split saves 0.147014 of drag by giving up 0.285215 of return. Spreading the cap does lower the variance, which is what diversifying is for. But the drag grows with the square of the leverage, so under a tight cap it is small at any allocation, and so is the saving. The return grows in proportion to the leverage, and each unit of the cap earns its own strategy’s mean, twice as high on strategy 2.

At the curve’s other end, everything on strategy 1 grows at 0.4648, less than half the corner’s rate. Against the 2.135068 the uncapped Kelly leverages would earn, the proportional split keeps 0.382563 of that rate and the corner 0.447292 of it. Both fall far short, because the cap allows 2 of the 9.335829 Kelly asks for.

## Lesson 3: the printed 0.96 depends on a rounding mode

The growth rate at the corner is exactly 191/200, which is 0.955. Chan prints 0.96. At two decimals 0.955 is a tie, halfway between 0.95 and 0.96, and three rounding rules split on it.

1. **Round half up**, the rule taught in school, gives 0.96.
2. **Round half to even**, which sends a tie to the even last digit, gives 0.96.
3. **Round half down** gives 0.95.

So the printed digit lands under two rules and cannot say which one Chan used. The trap is in code. A floating-point number cannot hold 0.955 exactly, and the nearest one it can hold sits just below the tie. Python’s `f"{g:.2f}"` and `round(g, 2)` both see a number below halfway and print 0.95. A report that formats the corner the obvious way puts 0.95 beside the book’s 0.96, and reads as a miss for a figure that lands. This repository’s run prints the corner at three decimals for that reason.

## Lesson 4: drop the bound and the best allocation shorts a winning strategy

The slope in Lesson 2 is a straight line in F2, so the growth rate along F1 = 2 − F2 is a parabola, and a parabola has a top. Solving for it without keeping F2 between 0 and 2 finds it at F2 = 2.289321 and F1 = −0.289321, growing at 0.962956. That is higher than the corner’s 0.955, and it is the hollow marker on the dashed part of the figure.

The allocation is not allowed. F1 is negative, a short position in strategy 1, so the gross leverage, the short plus the long, is 2.578643, over the cap of 2. The line F1 + F2 = 2 fixes the net leverage, and only between F2 = 0 and 2 does it also fix the gross. Location 3268 is explicit that the cap is on gross leverage, “not the net leverage”.

A solver handed the line and no bounds reports this point. The mistake is easy to overlook, because 0.962956 rounds to the same 0.96 the book prints for the corner. The sign of F1 gives it away. Strategy 1 has a positive mean, so a short in it loses money on average, and the only reason to hold one here is to make room in F1 + F2 for more of strategy 2. A cap on the gross forbids exactly that.

## Lesson 5: everything on one strategy stays best only below a cap of 2.45

Location 3268 states the example’s upshot. When the cap “is much smaller than” the total Kelly leverage, it is often best to put most or all of the buying power on the strategy with the highest mean excess return. Location 3287 says the same with “the highest growth rate”. On these inputs strategy 2 has both. Its Sharpe ratio is higher, 1.714286 against 1.153846, and with the whole cap of 2 on it alone it grows at 0.955 against strategy 1’s 0.4648. So the example cannot say which of the two Chan means when they disagree.

On these inputs the “most” holds at every cap up to the total Kelly leverage. Strategy 2’s share of the best long-only split is the whole cap at 2.448980, 0.882 at a cap of 3, 0.750 at 4 and 0.525 at the total of 9.335829. What a tighter cap adds is the “all”, which is how location 3287 puts it: “apply all of our buying power” on one strategy.

The corner stays best while the slope of the growth rate at the corner is still positive. At the corner that slope is strategy 2’s extra mean less the drag that its last unit of leverage adds, and it falls as the cap rises. It reaches zero at

```math
F_{\max} = \frac{m_2 - m_1}{c_{22} - c_{12}}
```

where m1 and m2 are the means, c22 is strategy 2’s variance and c12 is the covariance, which is 0 here. That cap is 2.448980. Below it, everything on strategy 2 is best. Above it, the best allocation holds both strategies. At a cap equal to the total Kelly leverage of 9.335829 it returns the Kelly pair, 4.437870 and 4.897959.

So on Chan’s inputs, everything on strategy 2 is best only while the cap is below 0.262321 of the total, about a quarter. The threshold is a formula in the means and the covariance, so a trader can compute it rather than guess. Two conditions limit it.

1. The strategy with the higher mean must have a variance above the two strategies’ covariance. Otherwise the slope at the corner does not fall as the cap rises, and the formula names no largest cap.
2. It marks only where everything on that strategy stops beating the other long-only ways to spend the whole cap. Lesson 6 shows a short can beat all of them.

## Lesson 6: long-only is the answer here and not in general

The search along the line looks only at long positions, F1 and F2 both at least 0, the range Chan plots. On Chan’s inputs that loses nothing. A search over every allocation whose gross leverage is 2, short positions included, finds the same corner at 0.955.

A strong positive correlation breaks that. Take two strategies with mean excess returns of 0.05 and 0.30, a volatility of 0.30 each, a correlation of 0.95, and a cap of 4. These inputs are this repository’s, built to test the limit, and are not Chan’s.

1. **The best long-only allocation** holds strategy 2 alone at its own Kelly leverage, 0.30 / 0.30², which is 3.333333. That sits inside the cap and grows at exactly 0.5. Spending the whole cap of 4 on strategy 2 grows at only 0.48.
2. **A short hedge inside the same cap** holds 1.002849 of strategy 1 short against 2.997151 of strategy 2 long, a gross of 4, and grows at 0.656501.

Set the hedge against the whole cap on strategy 2, which earns a return of 1.2 and pays a drag of 0.72. The hedge earns 0.849003 and pays 0.192501. It gives up 0.350997 of return in two parts.

1. **The short itself** loses strategy 1’s mean on 1.002849 of leverage, 0.050142.
2. **The displaced long** loses 0.300855, strategy 2’s mean on the 1.002849 of the gross cap that the short now uses.

Because the two strategies move together so closely, the short cancels most of strategy 2’s variance, and the drag falls by 0.527499. That saving is larger than all the return given up, so the hedge grows faster. Lesson 4’s short broke the gross cap. This one stays inside it.

So the corner’s win in Example 8.2 is a property of its inputs, two uncorrelated strategies with positive means, under a cap below 2.45. This repository’s capped search says it is long-only for that reason, and its tests hold a case where the long-only restriction costs growth.

## What this replication cannot say

Two questions are beyond it.

1. **Whether Equation 8.3 prints a number.** The highlights this repository works from do not capture the equation, so the 2.135068 growth rate at the uncapped Kelly leverages has no published figure to land against. That waits on the book itself.
2. **Anything about a real pair of strategies.** Every input is hypothetical, and the returns are Gaussian by assumption. Whether a cap makes a real second strategy worth dropping depends on means and variances estimated from data. Location 3235 warns that “we will inevitably suffer estimation errors” in those estimates, and the SPY post shows how far the choice of years alone can move a Kelly leverage.

## What this means for a trader

One habit for each lesson.

1. **Know what a check can test.** A check of arithmetic on stated inputs confirms the arithmetic and nothing about any market.
2. **Compare allocations by growth rate.** Under a tight cap, diversifying saves little drag and can give up much more return.
3. **Print one more decimal when a figure sits on a tie.** At the tie’s own precision, the rounding rule decides the digit, and a figure that lands can read as a miss.
4. **Check a solver’s answer against its constraint.** With uncorrelated strategies, a short in one with a positive mean is the sign the solver broke the cap.
5. **Compute the threshold instead of trusting “much smaller”.** It holds when the higher-mean strategy’s variance exceeds the covariance, and it says only where everything on that strategy stops beating the other long-only ways to spend the whole cap.
6. **Treat long-only as an assumption.** With strongly correlated strategies, a short hedge inside the cap can beat every long-only split.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 8.1 and 8.2 and Kindle locations 3210, 3216, 3228, 3235, 3259, 3268 and 3287.
2. Khandani, A. E., & Lo, A. W. (2007). What happened to the quants in August 2007? Working paper, MIT.
3. Thorp, E. O. (1997). The Kelly criterion in blackjack, sports betting, and the stock market. Paper presented at the 10th International Conference on Gambling and Risk Taking, Montreal.

*Not investment advice. Code: [the two examples](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/kelly_allocation.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/kelly_allocation_figures.py), with the checks behind [the examples’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_kelly_allocation.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_kelly_allocation_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-20-constant-leverage-and-capped-kelly-allocation-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
