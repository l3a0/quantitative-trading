# Risk parity’s numbers reproduce on SPY and AGG, and its claim does not

*Qian’s mix of 23% stocks and 77% bonds, levered 1.8 times, comes out close on 2003 to 2026 data. At a 4% cash rate the better return for its risk that it was meant to deliver goes to 60/40, and no cash rate of zero or more makes risk parity a clear winner.*

## Why a close match is not enough

Ernest Chan’s *Quantitative Trading* (Chan, 2021) reports an argument by Edward Qian of PanAgora Asset Management, in a passage on why a lower-risk portfolio can be worth levering. A portfolio split 60% stocks and 40% bonds, usually called **60/40**, is balanced in its capital and nowhere near balanced in its risk, because stocks swing several times as hard as bonds. Qian’s alternative, **risk parity**, weights each asset so that it carries the same share of the risk, then borrows to bring the whole portfolio back up to 60/40’s risk.

Chan quotes the result in one sentence. At the same risk as 60/40, Qian recommends 23% stocks and 77% bonds, levered 1.8 times, to earn a higher **Sharpe ratio**. The Sharpe ratio is the return above cash divided by the size of the swings, so a higher one means more reward per unit of risk.

This replication runs the same calculation on SPY, the fund that tracks the S&P 500, and AGG, a fund that tracks the aggregate US bond market, from September 2003 to September 2026. The allocation comes out at 21.8% stocks against Qian’s 23%, and the leverage at 1.98 against his 1.8. Both are close. At the 4% cash rate Chan uses elsewhere in the book, the Sharpe ratio claim goes the other way. 60/40 earns 0.41 and levered risk parity 0.19.

Two earlier replications of Chan’s examples, of a cointegrated pair and of the Kelly leverage on SPY, showed the opposite pattern. Their figures moved a little and their central claims held. This post explains how risk parity works and draws six lessons from a case where the figures hold and the conclusion fails. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## How risk parity works

A portfolio’s risk here is the standard deviation of its daily returns, stated as a yearly figure and called **volatility**. From 2003 to 2026, SPY’s volatility is 18.55% and AGG’s is 5.17%, so stocks swing 3.59 times as hard as bonds.

Call stocks asset 1 and bonds asset 2, with weights `w₁` and `w₂` and volatilities `σ₁` and `σ₂`. Their **correlation** `ρ` runs from −1 to +1 and measures how far the two tend to move together. The portfolio’s variance, the square of its volatility, is:

```math
\sigma_p^2 = w_1^2 \sigma_1^2 + w_2^2 \sigma_2^2 + 2 \rho\, w_1 w_2 \sigma_1 \sigma_2
```

The first term belongs to stocks, the second to bonds, and the third is shared. Giving each asset its own term plus half of the shared one splits the variance into two **risk contributions**, which add up to the whole. Each asset’s share of risk is its contribution divided by the total.

From 2003 to 2026 the correlation between SPY and AGG is −0.0002, close enough to zero that the shared term is negligible. Each asset’s risk is then its weight squared times its variance, and its share is that divided by the two added together. At 60/40, stocks contribute 0.6² × 18.55%² and bonds 0.4² × 5.17%². The first is about 29 times the second, so stocks carry 96.7% of 60/40’s risk and bonds 3.3%. Qian’s own data gave 93% to stocks.

Risk parity picks the weights that make the two contributions equal. Setting them equal puts the shared term on both sides, where it cancels, whatever the correlation is:

```math
w_1^2 \sigma_1^2 = w_2^2 \sigma_2^2 \quad\Rightarrow\quad w_1 \sigma_1 = w_2 \sigma_2
```

So each weight shrinks as its asset’s volatility grows, and an asset twice as volatile gets half the weight. With weights that sum to 1, the stock weight is `σ₂ / (σ₁ + σ₂)`, which is 5.17 divided by the sum of the two, or 21.8%. Bonds get 78.2%.

![Four horizontal bars for SPY and AGG from 2003 to 2026. 60/40 splits capital 60% SPY and 40% AGG and splits risk 96.7% SPY and 3.3% AGG. Risk parity splits capital 21.8% SPY and 78.2% AGG and splits risk 50% each.](../docs/figures/risk_parity_capital_and_risk.png)

*60/40 is nearly an all-stock portfolio when measured by risk. Risk parity balances the risk by moving most of the capital into bonds.*

Holding mostly bonds leaves risk parity about half as volatile as 60/40. Qian’s second step is to lever it until its volatility matches 60/40’s 11.32%, which here takes leverage of 1.98. At 1.98, every \$100 of the trader’s money holds \$43 of SPY and \$155 of AGG, and the extra \$98 is borrowed at the cash rate.

Matching the volatilities is what makes the comparison fair. With both portfolios at 11.32% volatility, the difference in their Sharpe ratios is the difference in their mean returns above cash, divided by 11.32%. So whichever portfolio earned more above cash has the higher Sharpe ratio.

Leverage scales a portfolio’s return above cash and its volatility by the same factor, so it leaves the Sharpe ratio unchanged. Levering risk parity makes the comparison fair, and it cannot change the result. Risk parity beats 60/40 at matched volatility exactly when the unlevered mix already has the higher Sharpe ratio.

Here are Qian’s figures beside the ones this replication computes. Qian (2005) used monthly returns on the Russell 1000 stock index and the Lehman Aggregate Bond Index from 1983 to 2004, so the two columns cover different years and different stock indices.

```math
\begin{array}{l|r|r}
\text{Quantity} & \text{Qian, 1983 to 2004, cash at bill rates} & \text{SPY and AGG, 2003 to 2026, cash at 4\%} \\ \hline
\text{Stock volatility} & 15.1\% & 18.55\% \\
\text{Bond volatility} & 4.6\% & 5.17\% \\
\text{Stock-bond correlation} & 0.2 & -0.0002 \\
\text{Sharpe ratio, stocks} & 0.55 & 0.45 \\
\text{Sharpe ratio, bonds} & 0.80 & -0.18 \\
\text{Stocks' share of 60/40's risk} & 93\% & 96.7\% \\
\text{Risk-parity stock weight} & 23\% & 21.8\% \\
\text{Leverage to match 60/40} & 1.8 & 1.98 \\
\text{Sharpe ratio, 60/40} & 0.67 & 0.41 \\
\text{Sharpe ratio, levered risk parity} & 0.87 & 0.19
\end{array}
```

The bond Sharpe ratio is where the two columns part. A negative Sharpe ratio means AGG earned less than the assumed cash rate, and Lesson 3 explains why that decides the comparison.

## Lesson 1: the numbers landed close and the claim did not survive

The allocation is about a point off Qian’s and the leverage about 0.2 above his. The method did what it says, too. At the 21.8% weight, each asset carries exactly 50% of the risk. Judged on those figures alone, the replication would pass.

Those figures were meant to back the Sharpe ratio claim, and it fails. At the 4% cash rate, 60/40 earns 0.41 and levered risk parity 0.19, a gap of 0.22 against risk parity. In mean returns above cash, 60/40 earns 2.46 percentage points a year more at the same volatility.

A gap that size could still be luck. The standard check is a **t-statistic**. It divides the average daily difference between the two portfolios’ returns by how far that average would typically wander by chance. A t-statistic beyond 2 in either direction means a gap that large would arise by chance less than 5% of the time, the usual bar for naming a winner. The difference here is risk parity minus 60/40, so a negative t-statistic favours 60/40. Newey and West (1987) give a version that allows for each day’s return being related to the days before it, and this post uses it throughout. Here that version comes to −2.17, so at the 4% rate the 23 years are enough to name 60/40 the winner. The plain version, which treats each day as unrelated to the last, is −1.75 and would not clear the bar. Daily portfolio returns are related from one day to the next, which is why the adjusted version is the one to use, and the verdict at 4% rests on it.

## Lesson 2: Qian’s weights and leverage are really a volatility ratio and a correlation

Risk parity sets `w₁σ₁ = w₂σ₂`, so Qian’s 23-77 says his stocks were 77 / 23, or 3.3 times as volatile as his bonds. Two significant figures is all he printed. Any weights that round to 23 and 77 put the ratio between 3.26 and 3.44. Dividing the two volatilities in his paper gives 3.28, inside that band. On SPY and AGG the ratio is 3.59. So the miss of about a point on the weight is the visible sign that SPY and AGG’s volatility ratio falls outside anything his rounded weights allow.

The leverage carries a second hidden input. Once the weights fix the volatility ratio, the leverage that matches 60/40 depends only on the correlation. The shared term is largest beside the other two when `w₁σ₁` equals `w₂σ₂`, which is what risk parity sets. In 60/40, stocks’ own term is about 29 times bonds’ and dwarfs it. So a change in correlation moves risk parity’s variance by a larger fraction than it moves 60/40’s. A higher correlation therefore raises risk parity’s volatility proportionally more, and it needs less leverage to reach 60/40’s. On his 23-77 weights, 1.8 corresponds to a correlation of 0.16, and his paper prints 0.2. That correspondence is loose, though. Letting both his weights and his leverage vary within their rounding puts the correlation anywhere from −0.01 to +0.37, wide enough to include both zero and a clearly positive correlation.

So Qian’s 23-77 and 1.8 describe the stocks and bonds of 1983 to 2004 rather than a rule for all time. Lesson 6 shows both inputs moving within the SPY and AGG data.

## Lesson 3: balancing risk does not balance return

Equal risk says nothing about the return each unit of risk earns, and leverage cannot change a Sharpe ratio. So the comparison comes down to the Sharpe ratios of the two funds inside the mix.

Qian’s paper states that risk parity is the best mix of risk and return when the assets earn the same Sharpe ratio and their returns are uncorrelated. In his 1983 to 2004 data, bonds earned more per unit of risk than stocks did, not merely the same. Treasury bills are short-term US government debt and the usual stand-in for cash. Bonds earned 3.7% a year above them, at a Sharpe ratio of 0.80 against 0.55 for stocks. So his levered risk-parity portfolio beat 60/40 by 2 points a year at the same risk.

On SPY and AGG the condition fails badly. SPY averaged 12.36% a year and AGG 3.09%. Against the 4% cash rate, SPY earned 8.36% a year above cash, a Sharpe ratio of 0.45, and AGG earned 0.91% below it, a Sharpe ratio of −0.18. A portfolio with 78.2% of its capital in AGG earns 1.11% above cash before leverage, and levering it 1.98 times lifts that to 2.20%. 60/40, with only 40% in AGG, earns 4.65%. The difference, 2.46 points before the two returns are rounded, divided by the shared 11.32% volatility, is the 0.22 by which 60/40 wins.

The bar risk parity has to clear can be sized. With the correlation near zero, each leg of risk parity carries the same risk, so its Sharpe ratio is about 0.71 times the sum of the two funds’ Sharpe ratios. 60/40’s is about 0.98 times stocks’ plus 0.18 times bonds’. So risk parity wins only when bonds’ Sharpe ratio is more than about half of stocks’. Qian’s 0.80 against 0.55 clears that easily, and AGG’s −0.18 against SPY’s 0.45 misses it badly.

## Lesson 4: the assumed cash rate decides the winner over the whole period

A Sharpe ratio needs a cash rate, and this replication has no record of what Treasury bills paid from 2003 to 2026. Bill rates are free to download, but this replication uses only data committed alongside its results, and recording a bill-rate series is work not yet done. It takes the 4% Chan sets in his Kelly example, as a choice rather than a measurement. Qian measured returns above the three-month Treasury-bill rate actually paid in each month.

The choice tilts the result by an amount that follows exactly from the borrowing. The levered portfolio borrows \$0.98 for every dollar of the trader’s own money, and 60/40 borrows nothing. So each percentage point cut from the assumed rate adds 0.98 points a year to risk parity’s return above cash, relative to 60/40. Closing the 2.46-point gap takes a rate about 2.5 points lower, and the two Sharpe ratios tie at 1.50%. Below that, risk parity has the higher Sharpe ratio over the whole period.

The verdict at 4% is also close to the edge of what the data can settle. The t-statistic moves with the rate in a straight line, and it reaches −2 at an assumed 3.80%. In the other direction, even at a rate of zero, risk parity’s lead over the whole period has a t-statistic of only +1.30, too small to name it the winner.

Whether Treasury bills averaged above or below 1.50% from 2003 to 2026 roughly decides which portfolio had the higher Sharpe ratio. Answering that needs a bill-rate series this replication does not hold.

## Lesson 5: judged on weights from earlier years, risk parity still loses the later period

60/40’s weights are fixed in advance and use no data. Risk parity computes its weights from measured volatilities. Weights computed from the same years that then score them fit every one of those days, an advantage 60/40 never gets.

So the replication splits the period at 16 March 2022, the day the Federal Reserve made the first of its 2022 run of rate rises. It fixed the date before computing any result, and took it from an outside event rather than from the prices. The earlier period runs from 2003 to the day before the rise, and the later period from the day after it to 2026. Weights for the later period come from the earlier one, which is data a trader would have held on the day.

Of the three periods, meaning the whole 23 years and its two parts, the later period is where risk parity does worst. At the 4% rate, 60/40 earns a Sharpe ratio of 0.51 and risk parity 0.01, a gap of 0.50, with a t-statistic of −2.20. Weights computed inside that period would have narrowed the gap to 0.38, with 60/40 still ahead. So most of the loss comes from the period rather than from the method, and the split keeps the part that is the method’s from flattering risk parity. The gap is wide enough that only a rate of −4.43% would tie the two, so no positive rate changes the winner there. The t-statistic is less secure. Like the whole period’s, it moves with the rate in a straight line. It reaches −2 at an assumed 3.25%, so below that rate the later period no longer clears the usual bar, even though 60/40 keeps the higher Sharpe ratio.

A second caution applies to the t-statistic. The weights come from the earlier period, but the leverage that matches 60/40’s volatility is measured inside the later one. Neither Sharpe ratio depends on the leverage, so the gap of 0.50 stays put. The t-statistic works on the daily difference in returns. More leverage makes that difference swing harder but barely moves its average, because risk parity earned almost nothing above cash in those years. At the leverage measured on the earlier period, 2.15 instead of 1.66, the t-statistic is −1.64, which is not enough to name a winner.

The earlier period on its own does not name a winner either. 60/40 wins it by 0.16, and a t-statistic of −1.35 is within what chance could produce. Its winner also flips with a smaller cut in the rate, since the two portfolios tie at 2.45% against 1.50% for the whole period. Those years lean the same way as the whole period without settling it.

## Lesson 6: the volatility ratio and the correlation changed when rates turned

The two inputs behind Qian’s figures differ between the two periods, as do the risk-parity weights each period would give on its own data.

- Before the 2022 rise, AGG’s volatility was 4.88%, SPY swung 3.87 times as hard, and the correlation was −0.07. Risk parity held 20.5% stocks and needed leverage of 2.15.
- After it, AGG’s volatility was 6.21%, SPY swung 2.76 times as hard, and the correlation was +0.24. Weights computed inside this period would hold 26.6% stocks. The portfolio actually scored kept the earlier 20.5% and needed leverage of 1.66 to match 60/40.

The volatility ratio fell from 3.87 to 2.76, and the two periods sit on opposite sides of the 3.26 to 3.44 band Qian’s weights allow. The near-zero correlation of −0.0002 over the whole period is a blend of a negative stretch before 2022 and a positive one after it, rather than a stable property of stocks and bonds.

Even weights computed inside the later period hold only 26.6% stocks, well short of 60/40’s 60%, so risk parity still leans away from stocks. The later period’s loss came from what AGG earned, 1.16% a year against the 4% rate, rather than from the correlation. The shifting inputs are Lesson 2’s point in the data: Qian’s weights and leverage belong to the period that produced them.

## What this replication cannot say

The replication tests Qian’s argument on funds and years it chose and wrote down before computing any number. It cannot say three things.

1. **Whether Qian’s own data reproduces his numbers.** He used the Russell 1000 from 1983 to 2004, and this replication uses SPY, which tracks the S&P 500, from 2003 on. AGG tracks his bond index but only opened in 2003. The two data sets overlap by at most 15 months.
2. **Whether costs change the result.** The book charges no trading costs and no borrowing spread above the cash rate, so neither does the replication. Both would hurt the levered, rebalanced risk-parity portfolio more than 60/40, so charging them could only move the result toward 60/40.
3. **Which allocation anyone should hold.** A replication uses its data to check someone else’s claim. It says whether the claim held on these funds over these years, and nothing about the next twenty years.

## What this means for a trader

Four habits follow from the lessons above.

1. **Check the claim, not only the numbers.** An allocation about a point off and a leverage about 0.2 off can still carry a conclusion that fails.
2. **Name the cash rate, and find the rate where the ranking flips.** Any comparison between a levered and an unlevered portfolio depends on the cash rate. Here the verdict over the whole period turns at 1.50%.
3. **Judge weights on data they did not see.** Weights computed from the very data they are judged on start with an advantage over fixed ones. Here, weights computed inside the later period would have narrowed risk parity’s loss there from 0.50 to 0.38.
4. **Report a ranking with its size and its t-statistic.** A statement that one Sharpe ratio beats another hides whether the gap is 0.01 or 0.50, and whether the data can tell the two portfolios apart.

At Chan’s 4% rate on SPY and AGG from 2003 to 2026, risk parity balances the risk exactly as described, and 60/40 still earns the higher Sharpe ratio at the same volatility. Whether balanced risk pays depends on bonds earning more than about half as much per unit of risk as stocks, which they did in Qian’s years and did not, at 4%, in these.

## References

- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley.
- Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703–708.
- Qian, E. (2005). *Risk Parity Portfolios: Efficient Portfolios Through True Diversification*. PanAgora Asset Management.

*Not investment advice. Code: [the risk parity calculation](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/risk_parity.py), and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/risk_parity_figures.py), with the checks behind [the calculation’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_risk_parity.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_risk_parity_figures.py), and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-4-risk-parity-against-6040-chans-quantitative-trading) that sets each of Chan’s and Qian’s figures beside the one reproduced here.*
