# A coin toss that pays on average and still loses money

*Why a trader should judge a bet by the compound growth rate of capital rather than by its expected value.*

## Why the average is the wrong yardstick

A fair coin pays \$110 on heads and costs \$100 on tails. On average a round pays \$5, so the bet looks worth taking. Play it 1,000 times from \$1,000, with the bet scaled to the account each round, and the typical trader ends with \$606.

Box 6.1 in Chapter 6 of Ernest Chan’s *Quantitative Trading* (Chan, 2021), titled “Loss aversion is not a behavioral bias”, uses this bet to argue that people who refuse it are right. Most performance numbers a trader sees are averages of one-period returns, like a backtest’s mean daily return or a bet’s expected value. A trader who reinvests does not collect that average. Capital compounds, so each round’s return multiplies what the last round left behind. For this bet, the average return and the growth of capital have opposite signs.

This post walks through the gamble, the two averages that disagree about it, and six lessons from reproducing it in code. The code behind every figure is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading). Where a number is Chan’s own printed figure rather than one worked out here, the post says so.

## The gamble

Chan borrows this setup from Daniel Kahneman’s *Thinking, Fast and Slow* (Kahneman, 2011) and changes the numbers to suit a trading account. The \$5 expected gain is half of \$110 less half of \$100. Chan notes that experiments show most people still refuse the bet. Behavioural finance calls that **loss aversion**, meaning a loss weighs more heavily than a gain of the same size, and treats it as a bias.

The argument works because Chan lets the payoff scale with capital, so an account that has doubled to \$2,000 wins \$220 or loses \$200. The stake is therefore always exactly a tenth of capital. Tails loses the stake, while heads pays 1.1 times it, which is 11% of capital. So each round multiplies the account by one of two numbers:

1. 1.11 on heads.
2. 0.90 on tails.

## Two averages that disagree

Chan credits the physicists Ole Peters and Murray Gell-Mann with the distinction that settles the question (Peters and Gell-Mann, 2016). There are two ways to average a repeated bet.

1. The **ensemble average** looks across many traders who each play the same number of rounds side by side. It asks what the crowd earns on average.
2. The **time average** follows one trader through many rounds in sequence. It asks what happens to a single account over time.

Start with the time average, because one pair of tosses already shows it. One head and one tail, in either order, leave the account at

```math
1.11 \times 0.90 = 0.999
```

of where it started. Starting from \$1,000, a win lifts the account to \$1,110, and the loss that follows takes 10% of that larger balance, which is \$111, leaving \$999. Over a long run a fair coin lands heads about half the time, so a typical trader gives up a tenth of a percent every two rounds.

The ensemble average is the mean simple return of one round, that is, the average percentage change in capital:

```math
m = \tfrac{1}{2}(0.11) + \tfrac{1}{2}(-0.10) = 0.005
```

The time average is the mean log return. A round’s **log return** is the natural log of the factor it multiplies capital by, so ln(1.11) for a head. Factors multiply across rounds while their logs add, which is why the mean log return is the rate that compounds:

```math
g = \tfrac{1}{2}\ln 1.11 + \tfrac{1}{2}\ln 0.90 = \tfrac{1}{2}(0.1043600) + \tfrac{1}{2}(-0.1053605) = -0.00050025
```

Chan prints a slightly different figure for `g`, because he uses the continuous approximation, a shortcut that gets more accurate as each round’s swings get smaller. It needs only the mean `m` and the standard deviation `s` of the one-round return. Each outcome sits 0.105 from the mean of 0.005, so `s` is 0.105 and the variance `s²` is 0.011025:

```math
g \approx m - \frac{s^2}{2} = 0.005 - \frac{0.011025}{2} = 0.005 - 0.0055125 = -0.0005125
```

To compare the two averages in one unit, convert the ensemble side to a log rate too. That gives ln(1.005) = 0.0049875 per round, against a time average of −0.00050025 per round. **The two averages have opposite signs.**

## Lesson 1: a positive expected value can shrink the typical account

Compound both rates from \$1,000 for 1,000 rounds. The ensemble mean reaches \$146,576. Compounding at the time-average rate gives \$606, a loss of 39%.

That \$606 is also where the median path ends. After an even number of rounds it is exactly the path with half heads and half tails. So a trader who plays 1,000 rounds has at least an even chance of finishing at \$606 or less, while the average across all traders is \$146,576.

A few lucky paths carry the gap. A trader who happens to throw far more heads than tails ends up enormously rich, and those rare fortunes pull the mean up. Only 4.7% of traders reach the mean. It describes the crowd’s total wealth, and it says very little about any one member of the crowd.

![Bar chart of the balances 1,000 rounds can reach between 440 and 560 heads, on a log axis from under a cent to over a hundred million dollars, with the share of traders reaching each. The bars form a bell centred near the median of \$606, which sits just left of the \$1,000 starting line. The ensemble mean of \$146,576 sits far out on the right tail. An inset zooms in on the 499-head and 500-head balances, \$492 and \$606, with the approximation’s \$599 falling between them.](../docs/figures/coin_flip_final_balances.png)

*The balances 1,000 rounds can reach from 440 to 560 heads, which covers all but 0.013% of traders, and the share who reach each. 56.3% end below the \$1,000 they started with. The inset’s \$599 is what the continuous approximation compounds to, which Lesson 5 explains.*

## Lesson 2: the rates stay constant and the capital diverges

Neither average changes with the number of rounds. The ensemble rate is 0.0049875 per round at round 10 and at round 1,000, and the time average is −0.00050025 at both. A report that prints the two rates shows a disagreement in sign and nothing more.

What pulls apart is the capital they compound into. The ratio of ensemble capital to time-average capital grows by the same factor every round. That factor is set by the difference between the two log rates, 0.005488 per round.

```math
\begin{array}{r|r}
\text{Rounds} & \text{Ensemble capital} \div \text{time-average capital} \\ \hline
10 & 1.06 \\
100 & 1.73 \\
250 & 3.94 \\
1{,}000 & 241.72
\end{array}
```

Over ten rounds the two capitals differ by 6%, which is why the bet looks harmless to someone who plays it a few times.

![Two hundred simulated capital paths over 1,000 rounds on a log scale, spreading from \$1,000 into a fan between a few cents and a few million dollars. A gold line for the ensemble mean climbs steadily to \$146,576. A red line for the median trader drifts down to \$606.](../docs/figures/coin_flip_capital_paths.png)

*Two hundred simulated traders. The gold line compounds the ensemble rate and the red line compounds the time average. The dashed line is the \$1,000 each trader started with. The 200 drawn here average \$21,664 at round 1,000, well short of the gold line, for the reason Lesson 6 gives.*

## Lesson 3: variance is a cost charged against growth

The continuous approximation says where the loss comes from. Compound growth is approximately the mean return minus half the variance:

```math
g \approx m - \frac{s^2}{2}
```

The second term is often called **volatility drag**, the growth a series loses purely because it moves around. For the coin, the drag `s²/2` is 0.0055125, slightly larger than the mean of 0.005, so the drag wins.

Chan makes the same point twice elsewhere in Chapter 6 (Chan, 2021), and both examples are his printed figures rather than numbers worked out here.

1. A stock that moves up or down 1% each minute with equal odds has a mean return of zero. Its compound growth is negative, about half a basis point, or 0.005%, a minute.
2. SPY, an exchange-traded fund that tracks the S&P 500, has a mean annual return of 11.23% in his example, and its compound growth rate without leverage is 9.8%. The 1.43-percentage-point gap is the drag.

So two strategies with the same mean return do not grow at the same rate. In the approximation, the one with lower variance compounds faster, and for a positive mean it is also the one with the higher **Sharpe ratio**. That ratio is the mean return divided by its standard deviation, `m/s`, the usual measure of return per unit of risk. Strictly it uses the return above a risk-free rate, which is zero for the coin.

## Lesson 4: the stake decides the sign

Write the growth rate as a function of the fraction `f` of capital at risk, with the win paying `b` times the stake. For Chan’s coin `b` is 1.1:

```math
g(f) = \tfrac{1}{2}\ln(1 + b f) + \tfrac{1}{2}\ln(1 - f)
```

Two stakes on this curve matter.

1. **Growth is zero** at a stake of `(b − 1)/b`, which is 1/11 for Chan’s coin. His stake of 1/10 sits just past that line, which is why the growth rate is a small negative number rather than a large one.
2. **Growth is highest** at `(b − 1)/(2b)`, which is 1/22. At that stake the time average is 0.0011351 per round.

![A curve of growth per round against the stake, from 0% to 11% of capital. It rises from zero to a peak of +0.0011351 at a stake of 1/22, falls back through zero at 1/11, and turns negative. Chan’s stake of 1/10 sits just below zero at −0.00050025. The region above zero is shaded green and the region below it red.](../docs/figures/coin_flip_growth_by_stake.png)

*The same coin at every stake. Growth peaks at 1/22 and turns negative past 1/11. Chan’s 1/10 sits on the negative side.*

On any fair coin, not only Chan’s, the best stake is exactly half the break-even stake. A coin whose win pays 1.5 times the stake peaks at a stake of 1/6 and breaks even at 1/3.

At the best stake the two averages still differ, but both are positive, and for a fair coin the time-average growth is exactly half the ensemble’s. So the factor the ensemble mean multiplies capital by is the square of the median trader’s factor. After 1,000 rounds from \$1,000 the median trader’s capital grows 3.11 times, to \$3,111. The ensemble mean grows by the square of that, to \$9,681, so the ratio between them is also 3.11, against 241.72 at Chan’s stake.

Chan calls the growth-maximising stake the **Kelly** stake. He gives its continuous form in Chapter 6 as a leverage, a number to multiply a position by. The leverage comes from that position’s mean return `m` and standard deviation `s`. Here the position is Chan’s bet of a tenth of capital, so `m` is 0.005 and `s` is 0.105, the same two figures as before:

```math
\frac{m}{s^2} = \frac{0.005}{0.105^2} \approx 0.4535
```

The formula says to scale Chan’s bet down to 0.4535 of its size, which is a stake of 0.04535 of capital. The exact best stake found above is 1/22, or 0.04545.

This approximation also carries the factor of two to any bet, not only a fair coin. Scaling a position by `k` gives growth of about `k·m − k²·s²/2`, which peaks at `k = m/s²` and falls back to zero at twice that.

Chan also gives the growth that the Kelly stake reaches (Chan, 2021), and it depends on nothing but the Sharpe ratio `S`. With the risk-free rate at zero, as it is for the coin, the best growth is:

```math
g^* \approx \frac{S^2}{2}
```

Scaling a bet up or down scales `m` and `s` by the same factor, so it never changes `S`. That is why the Sharpe ratio, and not the mean return, is what caps growth. The coin checks the formula. Its Sharpe ratio per round is 0.005 / 0.105, exactly 1/21, so the formula gives a best growth of 1/882, about 0.0011338 per round. The exact best, at a stake of 1/22, is 0.0011351.

## Lesson 5: the formula hides two choices, and one makes the loss nearly 12 times larger

Computing a growth rate from returns involves choices the formula `m − s²/2` does not state. Two of them matter here, and each produces a number that looks right but does not match Chan’s. The coin exposes both, because Chan printed four numbers that any method has to reproduce:

1. The \$5 expected gain.
2. The 0.005 mean.
3. The 0.105 standard deviation.
4. The −0.0005125 growth rate, from the continuous approximation.

He cites Example 6.1, earlier in Chapter 6, for the approximation, but the box itself does not show his work. The way to test how he computed the growth rate is to find the choices that reproduce all four numbers at once.

### Which standard deviation

A standard deviation can divide by the number of observations `n`, the population form, or by `n − 1`, the sample form. A sample’s own average sits closer to its data than the true mean does, so dividing by `n` understates the spread, and dividing by `n − 1` makes the variance correct on average. Over a few thousand daily returns the two barely differ. Over the coin’s two outcomes they differ a lot. Those two equally likely outcomes are the whole distribution rather than a sample of it, so the population form is the correct one.

The sample form gives 0.14849 rather than 0.105, and the growth rate becomes −0.006025, out by a factor of 11.8. It still prints as a small negative number, so nothing about it looks wrong. Software can also make the choice silently. Two Python libraries common in finance disagree: pandas’ `.std()` defaults to the sample form and numpy’s `std` to the population form. Name the convention when reporting a volatility, and check it when copying one.

### Exact or approximate growth

The exact rate is −0.00050025 and the approximation is −0.0005125. They differ at the second significant digit, and both are correct answers to slightly different questions. The exact rate is the log growth per round of this two-outcome coin. The approximation is the growth of a price that moves continuously, drifting at an average rate of `m` with a variance of `s²` per round.

The difference matters once the rate is compounded into a balance. Each head multiplies the balance by 1.11 and each tail by 0.90. Multiplication ignores order, so heads then tails leaves the same \$999 as tails then heads, and the balance depends only on how many tosses came up heads. Two rounds show how the counting works.

```math
\begin{array}{c|l}
\text{Heads in 2 rounds} & \text{Balance from } \$1{,}000 \\ \hline
0 & 1{,}000 \times 0.90 \times 0.90 = \$810.00 \\
1 & 1{,}000 \times 1.11 \times 0.90 = \$999.00 \\
2 & 1{,}000 \times 1.11 \times 1.11 = \$1{,}232.10
\end{array}
```

Two rounds allow three head counts, 0, 1 and 2, so three balances. In general, `n` rounds allow `n + 1` head counts. After 1,000 rounds the head count runs from 0 to 1,000, so 1,001 balances are possible, one for each head count `h`:

```math
C(h) = 1000 \times 1.11^{h} \times 0.90^{\,1000-h}, \qquad h = 0, 1, 2, \ldots, 1000
```

The two nearest the middle are \$492 for 499 heads and \$606 for 500. Compounded, the approximation gives \$599, which falls between them and so is a balance no sequence of tosses can produce. The exact rate compounds to \$606, the balance of the median trader, which is the trader the time average is meant to describe. Use the approximation to see where growth comes from, the mean less half the variance, and compound the exact rate to get a balance.

### Check the method, not only the result

The two choices that miss Chan’s figure are also a lesson in checking work. Landing on −0.0005125 matches his number, but a different formula could still produce it. Showing that the sample form gives −0.006025 and the exact rate gives −0.00050025, and that neither matches Chan, rules out the two alternatives a reader would most likely try. That narrows the method down without proving it. The narrowing matters because a wrong method can still print a plausible number, as the sample form does. A backtest checked only against its headline Sharpe ratio has the same blind spot.

## Lesson 6: a simulation of the coin can mislead in two ways

Traders test ideas by simulating them, in a backtest or a run of random scenarios. The coin is a rare case where the right answer is known exactly, so it shows how far a simulation can be trusted. Each run starts from a **seed**, a number that fixes the sequence of tosses the random generator produces. Recording the seed lets anyone repeat the run, provided the method that draws the tosses and the library version are recorded too, since a change to either can give different tosses from the same seed. The coin shows two ways a simulation misleads, and each has a counterpart when simulating a real strategy.

### Noise swamps a small edge

A strategy whose edge is small next to its swings is hard to measure by simulation, and the coin shows how hard.

One toss’s log return has a standard deviation of 0.10486, just under the 0.105 of its simple return. The number the simulation tries to measure is the time-average growth, about −0.0005 per round. Averaging `N` tosses shrinks the noise to `0.10486/√N`. That figure is the **standard error**, the typical size of the estimate’s error. At 100 rounds by 200 traders, 20,000 tosses in all, the standard error is 7.41e-4, larger than the growth itself. A million tosses bring it down to 1.05e-4, a fifth of the growth. So print the standard error beside a simulated growth rate, and do not trust a sign that sits within two standard errors of zero.

A small run can therefore land on the wrong side of zero. Three results show what the size of a run does.

1. At 100 rounds by 200 traders, the simulated time average comes out positive on 56 of the first 200 seeds. More than a quarter of runs say the losing bet wins.
2. At 1,000 rounds by 1,000 traders, it comes out negative on all 200.
3. The large run at seed 42 sits 4.955 standard errors below zero, well clear of the two-standard-error line.

![Two histograms on one horizontal axis of simulated time-average growth per round, each counting 200 seeds. The top one, for 100 rounds by 200 traders, spreads from about −0.0024 to +0.0015 and straddles zero, with the 56 seeds right of zero shaded red. The bottom one, for 1,000 rounds by 1,000 traders, is a narrow spike centred on the true growth of −0.0005, entirely left of zero.](../docs/figures/coin_flip_sign_by_run_size.png)

*The same simulation at two sizes, 200 seeds each. The small run’s spread is wider than the effect it measures, so 56 seeds land on the wrong side of zero. The large run’s spread is narrow enough that none do.*

The same noise is why this replication checks Chan’s printed figures against exact arithmetic, and uses simulation only to illustrate the argument.

### Average final wealth reads low

The ensemble side has a true growth per round of ln(1.005) = 0.0049875. One way to estimate it from a simulation is to average every trader’s final wealth, take the log, and divide by the number of rounds. With 1,000 traders playing 5,000 rounds each, that estimate sits below 0.0038 on every one of the first 20 seeds. It reads low because a few very lucky paths carry the true mean, as Lesson 1 showed, and a sample of 1,000 traders rarely draws them.

The other way averages the simple return of every toss and converts that average to a log rate. It needs no rare paths, and on the same 20 seeds it lands within 1e-4 of 0.0049875. A simulation that reports mean final wealth for a strategy can understate the ensemble growth the same way. For a single account, the time-average growth is the figure to read.

![A dot plot with two rows and one dot per seed for 20 seeds. The top row, the log of the mean final wealth, spreads from about 0.0023 to 0.0037, every dot well left of a vertical line at the true ensemble growth of 0.0049875. The bottom row, the mean of each toss’s return, is a tight cluster sitting on that line.](../docs/figures/coin_flip_ensemble_estimators.png)

*Two ways to estimate the ensemble growth from the same simulated tosses. Averaging final wealth reads low on every seed, while averaging each toss’s return lands on the true value.*

## What this means for a trader

Chan’s own summary is short: “take time average, not ensemble average, when evaluating real-world risks” (Chan, 2021). A trader has one account and plays in sequence, so the time average is the one that describes what happens to them.

The replication itself is exact arithmetic on a coin. It uses no historical prices, so it can say that Chan’s arithmetic reproduces and why his argument holds. It says nothing about any particular strategy. The [replication log](../docs/replication-log.md#entry-2-the-coin-flip-gamble-chans-quantitative-trading) sets each of Chan’s figures beside the one reproduced here.

Four habits follow from the lessons above.

1. **Judge a strategy by its compound growth rate.** A mean return is an ensemble number. Subtract the volatility drag before comparing two strategies.
2. **Choose the stake before judging the bet.** The same bet can shrink or grow capital depending on the stake. On a fair coin, and in the continuous approximation for any bet, a stake beyond twice the growth-maximising one turns growth negative however attractive the average looks.
3. **Report capital over several horizons.** Two rates at one horizon hide how far the capital they compound into drifts apart.
4. **Check how a number was computed.** Name the standard-deviation convention behind a volatility, and print the standard error beside a simulated growth rate.

The refusal Box 6.1 defends is a judgement about sizing. At a tenth of capital, loss aversion gives the right answer. At a twenty-second of capital, the same aversion would turn down a bet worth taking.

## References

- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley.
- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
- Peters, O., and Gell-Mann, M. (2016). Evaluating gambles using dynamics. *Chaos*, 26(2), 023103.

*Not investment advice. Code: [the gamble](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/coin_flip_growth.py) and [the charts](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/coin_flip_figures.py), with the checks behind [every number](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_coin_flip_growth.py) and [every chart](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_coin_flip_figures.py).*
