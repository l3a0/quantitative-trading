# A coin toss that pays on average and still loses money

*Six lessons from replicating Chan’s Example 6.1, on why a trader should judge a bet by the compound growth rate of capital rather than by its expected value.*

## Why the average is the wrong yardstick

Most performance numbers a trader sees are averages of one-period returns. A backtest reports a mean daily return, a fund reports a mean annual return, and a bet gets judged by its expected value. All of them answer the same question: what does one round pay, averaged over every way it could turn out?

A trader who reinvests does not collect that average. Capital compounds, so each round’s return multiplies what the last round left behind. Ernest Chan’s Example 6.1 in *Quantitative Trading* builds a bet where those two things disagree in sign. The expected value is positive, and a trader who keeps playing ends up poorer.

This post walks through the gamble, the two averages that disagree about it, and six lessons from reproducing it in [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading). Every number below that the repository computes is checked by a test that fails if the number changes, and the few that are Chan’s own printed figures say so.

## The gamble

Chan borrows the setup from Daniel Kahneman’s *Thinking, Fast and Slow* and changes the numbers to suit a trading account. A fair coin is tossed. Heads wins \$110 and tails loses \$100, starting from \$1,000 of capital.

The expected gain is \$5 a round, half of \$110 less half of \$100. Most people still refuse the bet. Behavioural finance calls that **loss aversion**, meaning a loss weighs more heavily than a gain of the same size, and treats it as a bias. Chan argues the refusal is correct.

The argument works because Chan lets the payoff scale with capital, so an account that has doubled to \$2,000 wins \$220 or loses \$200. The stake is therefore always exactly a tenth of capital. Tails loses the stake, while heads pays 1.1 times it, which is 11% of capital. So each round multiplies the account by one of two numbers:

1. 1.11 on heads.
2. 0.90 on tails.

## Two averages that disagree

Chan credits the physicists Ole Peters and Murray Gell-Mann with the distinction that settles the question. There are two ways to average a repeated bet.

1. The **ensemble average** looks across many traders who each play the same number of rounds side by side. It asks what the crowd earns on average.
2. The **time average** follows one trader through many rounds in sequence. It asks what happens to a single account over time.

Start with the time average, because one pair of tosses already shows it. One head and one tail, in either order, leave the account at

```math
1.11 \times 0.90 = 0.999
```

of where it started. Over a long run a fair coin lands heads about half the time, so a typical trader gives up a tenth of a percent every two rounds. Starting from \$1,000, a win lifts the account to \$1,110, and the loss that follows takes 10% of that larger balance, which is \$111.

The ensemble average is the mean simple return of one round:

```math
m = \tfrac{1}{2}(0.11) + \tfrac{1}{2}(-0.10) = 0.005
```

The time average is the mean log return, which is what compounds:

```math
g = \tfrac{1}{2}\ln 1.11 + \tfrac{1}{2}\ln 0.90 = \tfrac{1}{2}(0.1043600) + \tfrac{1}{2}(-0.1053605) = -0.00050025
```

Chan prints a slightly different figure for `g`, because he uses the continuous approximation. It needs only the mean `m` and the standard deviation `s` of the one-round return. Here `s` is 0.105, so the variance `s²` is 0.011025:

```math
g \approx m - \frac{s^2}{2} = 0.005 - \frac{0.011025}{2} = 0.005 - 0.0055125 = -0.0005125
```

To compare the two averages in one unit, convert the ensemble side to a log rate too. That gives ln(1.005) = +0.0049875 per round, against a time average of −0.00050025 per round. The two averages have opposite signs.

## Lesson 1: a positive expected value can shrink the typical account

Compound both rates from \$1,000 for 1,000 rounds. The ensemble mean reaches \$146,576. Compounding at the time-average rate gives \$606, a loss of 39%.

That \$606 is also where the median path ends. After an even number of rounds it is exactly the path with half heads and half tails. So a trader who plays 1,000 rounds has at least an even chance of finishing at \$606 or less, while the average across all traders is \$146,576.

The gap is carried by a few lucky paths. A trader who happens to throw far more heads than tails ends up enormously rich, and those rare fortunes pull the mean up. Almost nobody lives on those paths. The mean describes the crowd’s total wealth, and it says very little about any one member of the crowd.

![Bar chart of every balance 1,000 rounds can reach, on a log axis from under a cent to over a hundred million dollars, with the share of traders reaching each. The bars form a bell centred near the median of \$606, which sits just left of the \$1,000 starting line. The ensemble mean of \$146,576 sits far out on the right tail. An inset zooms in on the 499-head and 500-head balances, \$492 and \$606, with the approximation’s \$599 falling between them.](../docs/figures/coin_flip_final_balances.png)

*Every balance 1,000 rounds can reach, and the share of traders who reach it. 56.3% end below the \$1,000 they started with, and only 4.7% reach the ensemble mean.*

## Lesson 2: the rates stay constant and the capital diverges

Neither average changes with the number of rounds. The ensemble rate is +0.0049875 per round at round 10 and at round 1,000, and the time average is −0.00050025 at both. A report that prints the two rates shows a disagreement in sign and nothing more.

![Two hundred simulated capital paths over 1,000 rounds on a log scale, spreading from \$1,000 into a fan between a few cents and a few million dollars. A gold line for the ensemble mean climbs steadily to \$146,576. A red line for the median trader drifts down to \$606.](../docs/figures/coin_flip_capital_paths.png)

*Two hundred simulated traders. The gold line compounds the ensemble rate and the red line compounds the time average. The dashed line is the \$1,000 each trader started with. The 200 drawn here average \$21,664 at round 1,000, well short of the gold line, for the reason Lesson 6 gives.*

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

Over ten rounds the two views differ by 6%, which is why the bet looks harmless to someone who plays it a few times. The damage is in the length of the horizon.

## Lesson 3: variance is a cost charged against growth

The continuous approximation says where the loss comes from. Compound growth equals the mean return minus half the variance:

```math
g \approx m - \frac{s^2}{2}
```

The second term is often called **volatility drag**, the growth a series loses purely because it moves around. For the coin, the drag `s²/2` is 0.0055125, slightly larger than the mean of 0.005, so the drag wins.

Chan makes the same point twice elsewhere in the chapter, and both examples are his printed figures rather than numbers this repo computes.

1. A stock that moves up or down 1% each minute with equal odds has a mean return of zero. Its compound growth is negative, about half a basis point a minute (Kindle location 2822).
2. SPY’s mean annual return in his example is 11.23%, and its compound growth rate without leverage is 9.8% (location 2869). The 1.43-point gap is the drag.

So two strategies with the same mean return do not grow at the same rate. The one with lower variance compounds faster, and it is also the one with the higher **Sharpe ratio**. That ratio is the mean return divided by its standard deviation, `m / s`, the usual measure of return per unit of risk. Strictly it uses the return above a risk-free rate, which is zero for the coin. Holding the mean fixed and cutting the standard deviation raises the Sharpe ratio and lowers the drag together, so here the higher Sharpe ratio is the faster-growing strategy.

Lesson 4 shows the stronger form of this. Once the bet is sized well, the Sharpe ratio alone sets the best growth a strategy can reach, and the mean return drops out.

## Lesson 4: the stake decides the sign

Write the growth rate as a function of the fraction `f` of capital at risk, with the win paying `b` times the stake. For Chan’s coin `b` is 1.1:

```math
g(f) = \tfrac{1}{2}\ln(1 + b f) + \tfrac{1}{2}\ln(1 - f)
```

Two stakes on this curve matter.

1. **Growth is zero** at a stake of `(b − 1)/b`, which is 1/11 for Chan’s coin. His stake of 1/10 sits just past that line, which is why the growth rate is a small negative number rather than a large one.
2. **Growth is highest** at `(b − 1)/(2b)`, which is 1/22. At that stake the time average is +0.0011351 per round.

![A curve of growth per round against the stake, from 0% to 11% of capital. It rises from zero to a peak of +0.0011351 at a stake of 1/22, falls back through zero at 1/11, and turns negative. Chan’s stake of 1/10 sits just below zero at −0.00050025. The region above zero is shaded green and the region below it red.](../docs/figures/coin_flip_growth_by_stake.png)

*The same coin at every stake. Growth peaks at 1/22 and turns negative past 1/11. Chan’s 1/10 sits on the negative side.*

The best stake is exactly half the break-even stake, and that factor of two is a property of any even-odds coin rather than of Chan’s numbers. A coin whose win pays 1.5 times the stake peaks at a stake of 1/6 and breaks even at 1/3.

At the best stake the two averages still differ, but both are positive. After 1,000 rounds from \$1,000 the median path reaches \$3,111 and the ensemble mean reaches \$9,681, a ratio of 3.11 rather than 241.72. For an even-odds coin at the best stake, one trader’s log growth is exactly half the ensemble’s.

The growth-maximising stake is the **Kelly** stake. Chan gives its continuous form in the same chapter as a leverage, a number to multiply a position by, computed from that position’s mean return `m` and standard deviation `s`. Here the position is Chan’s bet of a tenth of capital, so `m` is 0.005 and `s` is 0.105, the same two figures the section on the two averages uses:

```math
\frac{m}{s^2} = \frac{0.005}{0.105^2} \approx 0.4535
```

The formula says to scale Chan’s bet down to 0.4535 of its size, which is a stake of 0.04535 of capital. The exact best stake found above is 1/22, or 0.04545.

Chan also gives the growth that the Kelly stake reaches (Kindle location 2849), and it depends on nothing but the Sharpe ratio `S`. With the risk-free rate at zero, as it is for the coin, the best growth is:

```math
g^* \approx \frac{S^2}{2}
```

Scaling a bet up or down scales `m` and `s` by the same factor, so it never changes `S`. That is why the Sharpe ratio, and not the mean return, is what caps growth. A strategy with twice the coin’s mean return and twice its standard deviation has the same Sharpe ratio, and so the same best growth. The coin checks the formula. Its Sharpe ratio per round is 0.005 / 0.105, exactly 1/21, so the formula gives a best growth of 1/882, about 0.0011338 per round. The exact best, at a stake of 1/22, is 0.0011351.

This changes what the layman’s refusal means. Refusing at a tenth of capital is correct. Accepting at a twenty-second of capital is also correct. Loss aversion here is a judgement about sizing, and at Chan’s size it gives the right answer.

## Lesson 5: two unstated formula choices can change a growth rate

Computing a growth rate from returns involves choices the formula `m − s²/2` does not state. Two of them matter here, and each produces a number that looks right but does not match Chan’s. The coin exposes both, because Chan printed enough figures to tell the right choice from the wrong one.

He prints four numbers for this example.

1. The \$5 expected gain.
2. The 0.005 mean.
3. The 0.105 standard deviation.
4. The −0.0005125 growth rate, from the continuous approximation.

He gives the approximation’s formula earlier in the chapter, but the example itself works no arithmetic. The only way to learn how he computed the growth rate is to find the choices that reproduce all four numbers at once.

### Which standard deviation

A standard deviation can divide by the number of observations `n`, or by `n − 1`. The second is the sample form. A sample’s own average sits closer to its data than the true mean does, so dividing by `n` understates the spread, and `n − 1` corrects for that. Over a few thousand daily returns the two barely differ. Over the coin’s two outcomes they differ a lot. Those two equally likely outcomes are the whole distribution rather than a sample of it, so the population form is the correct one.

The sample form gives 0.14849 rather than 0.105, and the growth rate becomes −0.006025, out by a factor of 11.8. It still prints as a small negative number, so nothing about it looks wrong. The choice can also flip without anyone making it, because pandas’ `.std()` defaults to the sample form and numpy’s `std` to the population form. Name the convention when reporting a volatility, and check it when copying one.

### Exact or approximate growth

The exact rate is −0.00050025 and the approximation is −0.0005125. They differ at the second significant digit, and both are correct answers to slightly different questions. The exact rate is the log growth per round of this two-outcome coin. The approximation is what that growth tends to when each round’s return is small.

The difference matters once the rate is compounded into a balance. Each head multiplies the balance by 1.11 and each tail by 0.90. Multiplication ignores order, so heads then tails leaves the same \$999 as tails then heads, and the balance depends only on how many tosses came up heads. Two rounds show how the counting works.

```math
\begin{array}{c|l}
\text{Heads in 2 rounds} & \text{Balance from } \$1{,}000 \\ \hline
0 & 1{,}000 \times 0.90 \times 0.90 = \$810.00 \\
1 & 1{,}000 \times 1.11 \times 0.90 = \$999.00 \\
2 & 1{,}000 \times 1.11 \times 1.11 = \$1{,}232.10
\end{array}
```

Two rounds allow three head counts, 0, 1 and 2, so three balances. The count always runs from zero heads up to one head per round, which is one more value than the number of rounds. After 1,000 rounds it runs from 0 to 1,000, so 1,001 balances are possible, one for each head count `h`:

```math
C(h) = 1000 \times 1.11^{h} \times 0.90^{\,1000-h}, \qquad h = 0, 1, 2, \ldots, 1000
```

The two nearest the middle are \$492 for 499 heads and \$606 for 500. Compounded, the approximation gives \$599, which falls between them and so is a balance no sequence of tosses can produce. The exact rate compounds to \$606, the balance of the median trader, which is the trader the time average is meant to describe. Use the approximation to see where growth comes from, the mean less half the variance, and compound the exact rate to get a balance.

### Checking the formula, not only the number

The two near misses are also what make a check worth running. A test that checks only −0.0005125 catches a changed number. Checking that the sample form gives −0.006025 and the exact form gives −0.00050025 catches a changed formula, which is the mistake that leaves a printed number looking plausible. A backtest checked only against its headline Sharpe ratio has the same blind spot.

## Lesson 6: three ways a simulation of the coin misleads

Traders test ideas by simulating them, in a backtest or a run of random scenarios. The coin is a rare case where the right answer is known exactly, so it shows how far a simulation can be trusted. Each run starts from a **seed**, the number a random generator starts from, which is recorded so the run can be repeated. Three things go wrong, and each has a counterpart when simulating a real strategy.

### Noise swamps a small edge

A strategy whose edge is small next to its swings is hard to measure by simulation, and the coin shows how hard. Print the standard error beside a simulated growth rate, and do not trust a sign that sits within two standard errors of zero.

The arithmetic behind that rule starts with one toss. Its log return has a standard deviation of 0.10486. The number the simulation tries to measure is the time-average growth, about −0.0005 per round. Averaging `N` tosses shrinks the noise to 0.10486 divided by √N. That figure is the **standard error**, the typical size of the estimate’s error. A million tosses still leave a standard error of 1.05e-4, a fifth of the growth being measured.

A small run can therefore land on the wrong side of zero. Three measurements show how large a run has to be.

1. At 100 rounds by 200 traders, the simulated time average comes out positive on 56 of the first 200 seeds. More than a quarter of runs say the losing bet wins.
2. At 1,000 rounds by 1,000 traders, it comes out negative on all 200.
3. The run in this post’s code sits 4.955 standard errors below zero, and its report prints that margin beside the estimate.

### Average final wealth reads low

The ensemble side has a true growth per round of ln(1.005) = 0.0049875. One way to estimate it from a simulation is to average every trader’s final wealth, take the log, and divide by the number of rounds. With 1,000 traders playing 5,000 rounds each, that estimate sits below 0.0038 on every one of the first 20 seeds. It reads low because the paths that carry the true mean, for the reason Lesson 1 gives, are too rare for a sample to draw.

The other way averages the simple return of every toss and converts that average to a log rate. It needs no rare paths, and on the same 20 seeds it lands within 1e-4 of 0.0049875. A simulation that reports mean final wealth for a strategy can understate it the same way. For a single account, the time-average growth is the figure to read anyway.

### A seed does not determine a run

numpy, Python’s numerical library, offers several ways to draw random tosses. From seed 7, four of them, `integers`, `random`, `binomial` and `standard_normal`, give four different sequences. Record the draw method beside the seed, or a rerun can produce different numbers from the same seed.

### Why the book’s figures are not checked by simulation

The first problem settles this. Chan prints seven decimals, and matching even the fifth decimal place would take about 110 million tosses. The repo therefore checks his figures against exact arithmetic, and uses the simulation only to show the sign.

## What this means for a trader

Chan’s own summary is short: “take time average, not ensemble average, when evaluating real-world risks.” A trader has one account and plays in sequence, so the time average is the one that describes what happens to them.

Three habits follow from the lessons above.

1. **Judge a strategy by its compound growth rate.** A mean return is an ensemble number. Subtract the volatility drag before comparing two strategies.
2. **Size before deciding.** The same bet can shrink or grow capital depending on the stake. On an even-odds bet, and in the continuous approximation for any bet, a stake beyond twice the growth-maximising one turns growth negative however attractive the average looks.
3. **Report capital over several horizons.** Two rates at one horizon hide the divergence, and the divergence is the risk.

The replication itself is exact arithmetic on a coin. It uses no historical prices, so it can say that Chan’s arithmetic reproduces and why his argument holds. It says nothing about any particular strategy. The [replication log](../docs/replication-log.md#entry-2-the-coin-flip-gamble-chans-quantitative-trading) records the verdict row by row.

*Not investment advice. Code: [the gamble](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/coin_flip_growth.py) and its [pinned tests](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_coin_flip_growth.py). Sources: Ernest P. Chan, Quantitative Trading, rev. ed., Example 6.1, Kindle locations 3166 to 3186. Daniel Kahneman, Thinking, Fast and Slow, 2011. Ole Peters and Murray Gell-Mann, “Evaluating gambles using dynamics”, Chaos 26, 023103, 2016.*
