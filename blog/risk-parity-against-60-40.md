# Risk parity’s numbers reproduce on SPY and AGG, and its claim does not

*Qian’s 23-77 allocation and 1.8 leverage land close on 2003 to 2026 data. The higher Sharpe ratio they were printed to support goes to 60/40 unless cash paid less than 1.50%.*

## Why a close match is not enough

Ernest Chan’s *Quantitative Trading* (Chan, 2021) reports an argument by Edward Qian of PanAgora Asset Management. A portfolio split 60% stocks and 40% bonds is balanced in its capital and nowhere near balanced in its risk, because stocks swing several times as hard as bonds. Qian’s alternative weights each asset so that it carries the same share of the risk, then borrows to bring the whole portfolio back up to 60/40’s risk. Chan quotes the result in one sentence: to earn a higher **Sharpe ratio**, the return above cash per unit of risk, at the same risk as 60/40, Qian recommends 23% stocks and 77% bonds, levered 1.8 times.

This replication runs the same calculation on SPY, the fund that tracks the S&P 500, and AGG, a fund that tracks the aggregate US bond market, from September 2003 to September 2026. The allocation comes out at 21.8% stocks against Qian’s 23%, and the leverage at 1.98 against his 1.8. Both are close. The Sharpe ratio claim those two numbers were printed to support goes the other way: 60/40 earns 0.41 and levered risk parity 0.19.

Earlier replications of Chan’s examples found the opposite split, where the figures moved and the conclusions held. This post explains how risk parity works and draws six lessons from a case where the figures hold and the conclusion fails. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## How risk parity works

A portfolio’s risk here is the standard deviation of its daily returns, stated as a yearly figure and called **volatility**. Over the span, SPY’s volatility is 18.55% and AGG’s is 5.17%, so stocks swing about 3.59 times as hard as bonds.

With weights `w₁` and `w₂` on two assets with volatilities `σ₁` and `σ₂`, and a correlation `ρ` between their returns, the portfolio’s variance, the square of its volatility, is:

```math
\sigma_p^2 = w_1^2 \sigma_1^2 + w_2^2 \sigma_2^2 + 2 \rho\, w_1 w_2 \sigma_1 \sigma_2
```

The first term belongs to stocks, the second to bonds, and the third is shared. Giving each asset its own term plus half of the shared one splits the variance into two **risk contributions**, which add up to the whole. Each asset’s share of risk is its contribution divided by the total.

Over this span the correlation between SPY and AGG is −0.0002, close enough to zero that the shared term vanishes. Each asset’s share of risk is then its weight squared times its variance, as a share of the sum. At 60/40, stocks contribute 0.6² × 18.55%² and bonds 0.4² × 5.17%². The first is about 29 times the second, so stocks carry 96.7% of 60/40’s risk and bonds 3.3%. Qian’s own data gave 93% to stocks.

**Risk parity** picks the weights that make the two contributions equal. Setting them equal, the shared term appears on both sides and cancels, whatever the correlation is:

```math
w_1^2 \sigma_1^2 = w_2^2 \sigma_2^2 \quad\Rightarrow\quad w_1 \sigma_1 = w_2 \sigma_2
```

So each weight is proportional to the inverse of its asset’s volatility. With weights that sum to 1, the stock weight is `σ₂ / (σ₁ + σ₂)`, which is 5.17 divided by 23.72, or 21.8%. Bonds get 78.2%.

![Four horizontal bars for SPY and AGG from 2003 to 2026. 60/40 splits capital 60% SPY and 40% AGG and splits risk 96.7% SPY and 3.3% AGG. Risk parity splits capital 21.8% SPY and 78.2% AGG and splits risk 50% each.](../docs/figures/risk_parity_capital_and_risk.png)

*60/40 is nearly an all-stock portfolio when measured by risk. Risk parity balances the risk by moving most of the capital into bonds.*

Holding mostly bonds leaves risk parity about half as volatile as 60/40. Qian’s second step is to lever it until its volatility matches 60/40’s 11.32%, which here takes 1.98 times equity. At 1.98, every \$100 of the trader’s money holds \$43 of SPY and \$155 of AGG, and the extra \$98 is borrowed.

Matching the volatilities is what makes the comparison fair. With both portfolios at 11.32% volatility, the difference in their Sharpe ratios is simply the difference in their mean returns above cash, divided by 11.32%. So the whole ranking comes down to one question: which portfolio earned more above cash.

Here are Qian’s figures beside the ones this replication computes. Qian (2005) worked monthly returns on the Russell 1000 stock index and the Lehman Aggregate Bond Index from 1983 to 2004, so the two columns cover different years and different stock indices.

```math
\begin{array}{l|r|r}
\text{Quantity} & \text{Qian, 1983 to 2004} & \text{SPY and AGG, 2003 to 2026} \\ \hline
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

## Lesson 1: the numbers landed close and the claim did not survive

The allocation is a point off Qian’s and the leverage is 0.18 above it. The method did what it says, too. At the 21.8% weight, each asset carries exactly 50% of the risk. Judged on those figures alone, the replication would pass.

The Sharpe ratio claim is what those figures were printed to support, and it fails. 60/40 earns 0.41 and levered risk parity 0.19, a gap of 0.22 against risk parity. In mean returns above cash, 60/40 earns 2.46 percentage points a year more at the same volatility.

A gap that size could still be chance. The test is a **t-statistic**: the average daily difference between the two portfolios, divided by its standard error, the typical size of the error in that average. The robust version, due to Newey and West (1987), widens the standard error to allow for each day’s return being related to the days before it. A robust t beyond 2 in either direction resolves the sign at the usual 5% level. Here it is −2.17, so over these 23 years the data does resolve the ranking, and it favours 60/40.

## Lesson 2: Qian’s two figures encode a volatility ratio and a correlation

Risk parity sets `w₁σ₁ = w₂σ₂`, so Qian’s 23-77 says his stocks were 77 / 23, or 3.3 times as volatile as his bonds. Two significant figures is all he printed. Any weights that round to 23 and 77 put the ratio between 3.26 and 3.44. Dividing the two volatilities in his paper gives 3.28, inside that band. On SPY and AGG the ratio is 3.59, outside it. A one-point miss on the weight is the visible sign of a volatility ratio that sits outside what his figures allow.

The leverage carries a second hidden input. Once the weights fix the volatility ratio, the leverage that matches 60/40 depends only on the correlation. On his 23-77 weights, 1.8 corresponds to a correlation of 0.16. His paper prints 0.2. That correspondence is loose, though. Letting both his weights and his leverage vary within their rounding puts the correlation anywhere from −0.01 to +0.37, which is most of the range a stock-bond correlation takes. A two-digit leverage says roughly what the correlation was, and no more.

Reading both figures as measurements explains why they cannot be constants. Lesson 6 shows both inputs moving.

## Lesson 3: balancing risk does not balance return

Equal risk says nothing about the return each unit of risk earns. Leverage multiplies the return above cash. When an asset earns less than cash, leverage multiplies a loss.

Qian’s paper states the condition itself. Risk parity is the best mix of risk and return when the assets earn the same Sharpe ratio and their returns are uncorrelated. In his 1983 to 2004 sample the bond index did better than that condition asks. It earned 3.7% a year above Treasury bills at a Sharpe ratio of 0.80, against 0.55 for stocks. So the portfolio that leaned on bonds won, and his levered risk-parity portfolio beat 60/40 by 2 points a year at the same risk.

On SPY and AGG the condition fails badly. SPY returned 12.36% a year and AGG 3.09%. Against Chan’s 4% cash rate, SPY earned 8.36 points above cash, a Sharpe ratio of 0.45, and AGG earned 0.91 points below it, a Sharpe ratio of −0.18. A portfolio with 78.2% of its capital in AGG earns 1.11% above cash before leverage, and levering it 1.98 times lifts that to 2.20%. 60/40, with only 40% in AGG, earns 4.65%. That difference, divided by the shared 11.32% volatility, is the 0.22 by which 60/40 wins.

## Lesson 4: the assumed cash rate decides the full-span ranking

A Sharpe ratio needs a cash rate, and the repository holds no Treasury-bill series. The replication uses Chan’s 4%, the rate he uses in his Kelly example, and states it as a choice rather than a measurement. Qian measured returns above the actual three-month Treasury-bill rate.

The choice is not neutral, and its direction is exact. The levered portfolio borrows \$0.98 for every dollar of equity, so it pays the cash rate on more money than 60/40 does. In returns above cash, each percentage point off the rate adds 0.98 points a year to risk parity’s side of the comparison. Closing the 2.46-point gap takes a rate about 2.5 points lower, and the two Sharpe ratios tie at an assumed rate of 1.50%. Below that, risk parity wins the full span.

Whether the Treasury-bill rate averaged above or below 1.50% from 2003 to 2026 roughly decides which portfolio had the higher Sharpe ratio, and answering it needs a bill-rate series this replication does not hold. The two sub-windows in Lesson 5 are less sensitive to the rate. Before 2022 the tie sits at 2.45%. After it, only a negative rate of −4.43% would tie them, so no positive rate reverses that window.

## Lesson 5: the weights must not see the window they are judged on

60/40 never looks at the data, since its weights are fixed by definition. Risk-parity weights come from measured volatilities. Weights fitted over a window and then judged on that same window have seen every day they are scored on, which gives risk parity an advantage 60/40 never gets.

The replication splits the span at 16 March 2022, the day the Federal Reserve made the first rate rise of its tightening cycle. The date was chosen before any result was seen, and it comes from an external event rather than from the price series. The falling-rates window runs from 2003 to the day before the rise, and the rising-rates window from the day after it to 2026. The weights for the rising window come from the falling window, which is data a trader would have held at the boundary.

That out-of-sample window is the worst of the three for risk parity. 60/40 earns a Sharpe ratio of 0.51 and risk parity 0.01, a gap of 0.50, with a robust t of −2.20. Refitting the weights inside the window would have helped risk parity, which is why it is not done.

The t needs one caution. The leverage is measured inside the window, and the t moves with it. At the leverage fitted on the falling window instead, the rising window’s t is −1.64, which does not resolve the ranking. The gap in Sharpe ratios does not move with the leverage at all, since leverage scales return and risk together.

The falling-rates window alone does not resolve its ranking either. 60/40 wins it by 0.16 with a robust t of −1.35. Those years point the same way as the full span without settling it.

## Lesson 6: the inputs moved with the regime

The volatility ratio and the correlation behind Qian’s two figures both changed between the windows.

1. Before the 2022 rise, SPY swung 3.87 times as hard as AGG and the correlation was −0.07. Risk parity held 20.5% stocks and needed leverage of 2.15.
2. After it, AGG’s volatility rose to 6.21% and the correlation turned positive at +0.24. The ratio fell to 2.76, risk parity held 26.6% stocks and needed leverage of 1.66.

The two windows sit on opposite sides of the 3.26 to 3.44 band Qian’s weights allow, so the quantity his 23-77 encodes moved by about a third within one pair of funds. The full span’s near-zero correlation of −0.0002 is an average of a negative stretch before 2022 and a positive one after it, rather than a stable property of stocks and bonds.

In the rising window the correction still pointed the same way. Risk parity held 26.6% stocks, well short of 60/40’s 60%. With stocks and bonds moving together and AGG earning 1.16% a year there, though, the bonds that risk parity levered earned too little to pay for the borrowing.

## What this replication cannot say

The replication tests Qian’s argument on instruments and years chosen here, fixed in writing before any number was computed. It cannot say three things.

1. **Whether Qian’s own data reproduces his numbers.** He used the Russell 1000 from 1983 to 2004, and SPY tracks the S&P 500 from 2003 on. AGG tracks his bond index but only opened in 2003. The two samples overlap by at most fifteen months.
2. **Whether costs change the result.** The book charges no trading costs and no borrowing spread above the cash rate, so neither does the replication. Both would hurt the levered, rebalanced risk-parity portfolio more than 60/40, so charging them could only widen 60/40’s lead.
3. **Which allocation anyone should hold.** A replication spends its sample checking someone else’s claim. It says whether the claim held on these funds over these years, and nothing about the next twenty.

## What this means for a trader

Four habits follow from the lessons above.

1. **Check the claim, not only the numbers.** An allocation and a leverage that land within a point and two tenths can still carry a conclusion that fails.
2. **Name the cash rate, and find the rate where the ranking flips.** Any comparison between a levered and an unlevered portfolio depends on the borrowing rate. Here the full-span verdict turns at 1.50%.
3. **Judge weights on data they did not see.** A fixed benchmark against weights fitted in-sample is not a fair race, and here the out-of-sample window was the one risk parity lost worst.
4. **Report a ranking with its size and its error bar.** A statement that one Sharpe ratio beats another hides whether the gap is 0.01 or 0.50, and whether the data can tell.

At Chan’s 4% rate on SPY and AGG from 2003 to 2026, risk parity balances the risk exactly as promised, and 60/40 still earns the higher Sharpe ratio at the same volatility. The premise holds and the payoff depends on bonds beating cash, which they did in Qian’s years and did not in these.

## References

- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley.
- Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703–708.
- Qian, E. (2005). *Risk Parity Portfolios: Efficient Portfolios Through True Diversification*. PanAgora Asset Management.

*Not investment advice. Code: [the risk parity calculation](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/risk_parity.py), and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/risk_parity_figures.py), with the checks behind [the calculation’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_risk_parity.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_risk_parity_figures.py), and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-4-risk-parity-against-6040-chans-quantitative-trading) that sets each of Chan’s and Qian’s figures beside the one reproduced here.*
