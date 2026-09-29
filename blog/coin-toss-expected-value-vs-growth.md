# A coin toss that pays on average and still loses money

*Six lessons from replicating Chan’s Example 6.1, on why a trader should judge a bet by the compound growth rate of capital rather than by its expected value.*

## Why the average is the wrong yardstick

Most performance numbers a trader sees are averages of one-period returns. A backtest reports a mean daily return, a fund reports a mean annual return, and a bet gets judged by its expected value. All of them answer the same question: what does one round pay, averaged over every way it could turn out?

A trader who reinvests does not collect that average. Capital compounds, so each round’s return multiplies what the last round left behind. Ernest Chan’s Example 6.1 in *Quantitative Trading* builds a bet where those two things disagree in sign. The expected value is positive, and a trader who keeps playing ends up poorer.

This post walks through the gamble, the two averages that disagree about it, and six lessons from reproducing it in [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading). Every number below that the repository computes is pinned in its test suite, and the few that are Chan’s own printed figures say so.

## The gamble

Chan borrows the setup from Daniel Kahneman’s *Thinking, Fast and Slow* and changes the numbers to suit a trading account. A fair coin is tossed. Heads wins \$110 and tails loses \$100, starting from \$1,000 of capital.

The expected gain is \$5 a round, half of \$110 less half of \$100. Most people still refuse the bet. Behavioural finance calls that **loss aversion**, meaning a loss weighs more heavily than a gain of the same size, and treats it as a bias. Chan argues the refusal is correct.

One detail makes the argument work. Chan lets the payoff scale with capital, so an account that has doubled to \$2,000 wins \$220 or loses \$200. The stake is therefore always exactly a tenth of capital, and each round multiplies the account by one of two numbers:

1. 1.11 on heads.
2. 0.90 on tails.

## Two averages that disagree

Chan credits the physicists Ole Peters and Murray Gell-Mann with the distinction that settles the question. There are two ways to average a repeated bet.

1. The **ensemble average** looks across many traders, each playing one round at the same moment. It asks what the crowd earns on average.
2. The **time average** follows one trader through many rounds in sequence. It asks what happens to a single account over time.

Start with the time average, because one pair of tosses already shows it. One head and one tail, in either order, leave the account at

```math
1.11 \times 0.90 = 0.999
```

of where it started. Over a long run a fair coin lands heads about half the time, so a typical trader gives up a tenth of a percent every two rounds. That is the whole mechanism. Starting from \$1,000, a win lifts the account to \$1,110, and the loss that follows takes 10% of that larger balance, which is \$111.

The ensemble average is the mean simple return of one round:

```math
m = \tfrac{1}{2}(0.11) + \tfrac{1}{2}(-0.10) = 0.005
```

The time average is the mean log return, which is what compounds:

```math
g = \tfrac{1}{2}\ln 1.11 + \tfrac{1}{2}\ln 0.90 = -0.00050025
```

Chan prints a slightly different figure for `g`, because he uses the continuous approximation. It needs only the mean `m` and the standard deviation `s` of the one-round return, which is 0.105 here:

```math
g \approx m - \frac{s^2}{2} = 0.005 - \frac{0.105^2}{2} = -0.0005125
```

To compare the two averages in one unit, convert the ensemble side to a log rate too. That gives ln(1.005) = +0.0049875 per round, against a time average of −0.00050025 per round. The two averages have opposite signs.

## Lesson 1: a positive expected value can shrink the typical account

Compound both rates from \$1,000 for 1,000 rounds. The ensemble mean reaches \$146,576. The time-average path reaches \$606, a loss of 39%.

The time-average path is also the median path. After an even number of rounds it is exactly the path with half heads and half tails. So a trader who plays 1,000 rounds has at least an even chance of finishing at \$606 or less, while the average across all traders is \$146,576.

The gap is carried by a few lucky paths. A trader who happens to throw far more heads than tails ends up enormously rich, and those rare fortunes pull the mean up. Almost nobody lives on those paths. The mean describes the crowd’s total wealth, and it says very little about any one member of the crowd.

## Lesson 2: the rates stay constant and the capital diverges

Neither average changes with the number of rounds. The ensemble rate is +0.0049875 per round at round 10 and at round 10,000, and the time average is −0.00050025 at both. A report that prints the two rates shows a disagreement in sign and nothing more.

What pulls apart is the capital they compound into. The ratio of ensemble capital to time-average capital grows by the same factor every round. That factor is set by the difference between the two log rates, 0.005488 per round.

| Rounds | Ensemble capital ÷ time-average capital |
| --- | --- |
| 10 | 1.06 |
| 100 | 1.73 |
| 250 | 3.94 |
| 1,000 | 241.72 |

For the first hundred rounds the two views barely differ, which is why the bet looks harmless to someone who plays it a few times. The damage is in the length of the horizon. So show a comparison like this as capital over several horizons. A single rate, or a single horizon, hides the part that matters.

## Lesson 3: variance is a cost charged against growth

The continuous approximation says where the loss comes from. Compound growth equals the mean return minus half the variance:

```math
g \approx m - \frac{s^2}{2}
```

The second term is often called **volatility drag**, the growth a series loses purely because it moves around. For the coin, the drag `s²/2` is slightly larger than the mean of 0.005, so the drag wins.

Chan makes the same point twice elsewhere in the chapter, and both examples are his printed figures rather than numbers this repo computes.

1. A stock that moves up or down 1% each minute with equal odds has a mean return of zero. Its compound growth is negative, about half a basis point a minute (Kindle location 2822).
2. SPY’s mean annual return in his example is 11.23%, and its compound growth rate without leverage is 9.8% (location 2869). The 1.43-point gap is the drag.

The practical reading: two strategies with the same mean return do not grow at the same rate. The one with lower variance compounds faster.

## Lesson 4: the stake decides the sign

The coin itself is not what makes this bet a loser. The size of the stake is. Write the growth rate as a function of the fraction `f` of capital at risk, with the win paying `b` times the stake. For Chan’s coin `b` is 1.1:

```math
g(f) = \tfrac{1}{2}\ln(1 + b f) + \tfrac{1}{2}\ln(1 - f)
```

Two stakes on this curve matter.

1. **Growth is zero** at a stake of `(b − 1)/b`, which is 1/11 for Chan’s coin. His stake of 1/10 sits just past that line, which is why the growth rate is a small negative number rather than a large one.
2. **Growth is highest** at `(b − 1)/(2b)`, which is 1/22. At that stake the time average is +0.0011351 per round.

The best stake is exactly half the break-even stake, and that factor of two is a property of any even-odds coin rather than of Chan’s numbers. A coin whose win pays 1.5 times the stake peaks at a stake of 1/6 and breaks even at 1/3.

At the best stake the two averages still differ, but they no longer fight. After 1,000 rounds from \$1,000 the median path reaches \$3,111 and the ensemble mean reaches \$9,681, a ratio of 3.11 rather than 241.72. For an even-odds coin at the best stake, one trader’s log growth is exactly half the ensemble’s.

The growth-maximising stake is the **Kelly** stake, and Chan gives its continuous form in the same chapter as `m / s²`. On this coin that formula says to hold 0.4535 of Chan’s stake, a stake of 0.04535 against the exact 1/22 of 0.04545.

This changes what the layman’s refusal means. Refusing at a tenth of capital is correct. Accepting at a twenty-second of capital is also correct. Loss aversion here is a judgement about sizing, and at Chan’s size it gives the right answer.

## Lesson 5: when the book gives no formula, the formula is what gets replicated

Chan prints four numbers for this example: the \$5 expected gain, the 0.005 mean, the 0.105 standard deviation and the −0.0005125 growth rate. He prints no formula. Matching the four numbers at once rules out two choices that look equally reasonable on the page.

1. **Sample versus population standard deviation.** Over two equally likely outcomes, dividing by `n − 1` instead of `n` gives 0.14849 rather than 0.105. The growth rate becomes −0.006025, out by a factor of 11.8, and it still prints as a small negative number, so nothing about it looks wrong. pandas’ `.std()` defaults to the sample form and numpy’s `std` to the population form, so the choice can flip by switching libraries.
2. **Exact versus approximate growth.** The exact rate is −0.00050025 and the approximation is −0.0005125. They differ at the fourth significant digit, and both are correct answers to slightly different questions. The exact rate is the one to compound. After 1,000 rounds the approximation gives \$599, a capital no sequence of tosses can produce, while the median path lands on \$606.

A test that pins only −0.0005125 holds a number. Pinning the near misses beside it holds the choice that produced the number.

## Lesson 6: a simulation has to be sized before it can be believed

A Monte Carlo run is the obvious way to show the effect. It turns out to be a poor way to measure it.

The log return of one toss has a standard deviation of 0.10486. A growth rate estimated from `N` tosses carries a standard error of 0.10486 divided by √N. A million tosses give a standard error of 1.05e-4, against an effect of about 5e-4. Chan prints seven decimals, and reaching even the fifth would take about 110 million tosses. So the book’s figures are pinned against the closed form, and the simulation only demonstrates the sign.

Even the sign needs a large enough run, and three measurements show how large.

1. At 100 rounds by 200 traders, the simulated time average comes out positive on 56 of the first 200 seeds. More than a quarter of runs show no effect at all.
2. At 1,000 rounds by 1,000 traders, it comes out negative on all 200.
3. The run the repo reports sits 4.955 standard errors below zero, and the report prints that margin beside the estimate.

The ensemble side is harder to see than it looks, for the reason Lesson 1 gives. Estimating it as the log of the mean final wealth misses the rare lucky paths that carry the mean. At 5,000 rounds by 1,000 traders, that estimate sits below 0.0038 on every one of the first 20 seeds, against a true value of 0.0049875. It gets worse as the runs get longer. Averaging the simple return of each toss instead recovers the true value to within 1e-4 on every one of those seeds.

A seed alone does not fix a run either. From seed 7, numpy’s `integers`, `random`, `binomial` and `standard_normal` give four different sequences of tosses. The draw method is part of what makes a simulated result reproducible, so name it beside the seed.

## What this means for a trader

Chan’s own summary is short: “take time average, not ensemble average, when evaluating real-world risks.” A trader has one account and plays in sequence, so the time average is the one that describes what happens to them.

Three habits follow from the lessons above.

1. **Judge a strategy by its compound growth rate.** A mean return is an ensemble number. Subtract the variance drag before comparing two strategies.
2. **Size before deciding.** The same bet can shrink or grow capital depending on the stake. Beyond twice the growth-maximising stake, growth turns negative however attractive the average looks.
3. **Report capital over several horizons.** Two rates at one horizon hide the divergence, and the divergence is the risk.

The replication itself is closed-form arithmetic on a coin. It reads no market data and spends no sample, so it can say that Chan’s arithmetic reproduces and why his argument holds. It says nothing about any particular strategy. The [replication log](../docs/replication-log.md#entry-2-the-coin-flip-gamble-chans-quantitative-trading) records the verdict row by row.

*Not investment advice. Code: [the gamble](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/coin_flip_growth.py) and its [pinned tests](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_coin_flip_growth.py). Sources: Ernest P. Chan, Quantitative Trading, rev. ed., Example 6.1, Kindle locations 3166 to 3186. Daniel Kahneman, Thinking, Fast and Slow, 2011. Ole Peters and Murray Gell-Mann, “Evaluating gambles using dynamics”, Chaos 26, 023103, 2016.*
