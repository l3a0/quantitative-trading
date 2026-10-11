# Three hypothesis tests on TU momentum: the book’s count lands, the script’s p-value is not the second test’s, and two checks added afterwards point at drift

*Chan asks of one momentum strategy how often chance alone would do as well, three ways. On his own file the book’s count of 1,166 lands, his script’s printed p-value does not, and his third test cannot fail as written. Two of three checks added after a trial run point at TU’s drift rather than its fat tails.*

## Why ask what chance alone would give

A backtest reports an average daily return, and the number means little on its own. A rule with no edge at all can earn a positive average over eight years if the market drifted its way or the days happened to fall well. The useful question is how often chance alone would do as well. Ernest Chan’s second book, *Algorithmic Trading*, sets out a framework for asking it in its first chapter (Chan, 2013, location 593). In paraphrase, it runs four steps.

1. Compute a **test statistic** from the backtest, such as its average daily return.
2. Suppose the true average is zero. The book calls that supposition “the null hypothesis”. It states, as a number, the claim that the rule has no edge.
3. Choose a probability distribution for the daily returns under that supposition.
4. Compute the probability that the statistic comes out at least as large as the backtest’s under that distribution. That probability is the **p-value**, and a small one lets a reader reject the null hypothesis.

The whole procedure is a **hypothesis test**. Step 3 decides the answer, and Example 1.1 shows how much. Chan takes his momentum strategy on TU, the two-year US Treasury note future, and builds the null three ways. One test finds chance matching the strategy in 1,166 of 10,000 tries. Another finds it in none of 100,000.

This repository reran all three tests on Chan’s own data file. Four results came out, three with verdicts and one without.

1. **The Gaussian test lands the script’s 2.93.**
2. **The second test lands the book’s count and misses the script’s p-value.** It gives 1,221 of 10,000 against the book’s 1,166, and a p-value of 0.122100 against the 0.027500 printed in the script’s comment.
3. **The third test as printed cannot fail.** Corrected, it still finds no shuffle as good as the real rule.
4. **Two of three checks added after a trial run point at TU’s drift, rather than its kurtosis, as what drives the second test.** That is a finding with no verdict.

**Every result here is exploratory.** Chan chose the strategy and the three tests, and reproducing his figures spends the 2004 to 2012 sample on his choices. The reproduction can say whether his numbers follow from his file. Before the random draws and pass marks of the run reported here were written down, a **trial run** executed the same tests on other draws, and its results were seen. The three added checks were chosen after that trial run, so they can motivate a registered test, one whose hypothesis is written down before any number exists, and cannot confirm anything.

The five lessons below say what the reproduction teaches. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule, the file and the three tests

**The rule.** Chapter 6’s strategy “buys (sells) the TU future if it has a positive (negative) 12-month return, and holds the position for 1 month” (Chan, 2013, location 642). The code counts 12 months as 250 trading days and a month as 25. Each day’s signal opens a slice of one unit, held 25 days, so up to 25 slices overlap. Each day’s return is yesterday’s position times today’s return on TU, divided by 25. TU appeared here once before, as the series [the USD.CAD post’s Hurst lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/usdcad-stationarity-lessons.md#lesson-3-h-misses-under-both-implementations-chans-code-uses) borrowed a setting from.

**The file.** Chan’s own MATLAB file `inputDataOHLCDaily_20120511.mat`, saved on 2012-05-12, holds TU’s closes for 2,000 trading days from 2004-06-01 to 2012-05-11. The rule’s **observed mean**, its average daily return over those days, is 6.626644e-05. Every test below asks how often chance alone reaches that number. The script that runs the tests is `TU_mom_hypothesisTest.m`, as published with the book’s code.

**The selection.** Chan picked the 250-day lookback and the 25-day hold from a table of correlations computed on the same closes, seven lookbacks against seven holds, 49 pairs in all. None of the three tests knows that. The section on what this replication cannot say returns to it.

The three tests differ only in how they build the null.

1. **The Gaussian test.** Suppose the daily returns are normal, with “a mean of zero and a standard deviation given by the sample standard deviation of the daily returns” (Chan, 2013, location 606). The statistic is then the mean divided by the standard deviation, times the square root of the number of days.
2. **The second test, simulating prices.** Generate “simulated historical price data and feed these simulated data into our strategy” (Chan, 2013, location 616). The script draws 2,000 daily returns for TU, builds a price from them, reruns the rule on that price and records its mean return. It repeats this 10,000 times. The draws share TU’s first four moments, listed after the three tests.
3. **The third test, resampling trades.** Keep the real returns, and “generate sets of simulated trades” instead (Chan, 2013, location 623), a method the book credits to Lo, Mamaysky and Wang (2000). The script shuffles the days on which the rule enters long or short, “randomizing the long and short entry dates” (Chan, 2013, location 669). Each shuffle moves the long and the short entry days together, so the rule keeps its 1,274 long entry days and 474 short entry days. It repeats this 100,000 times.

Each of the last two tests counts how many simulated means are at or above the observed mean. That count divided by the number drawn is the p-value. Chan reports that “1,166 have average strategy return greater than or equal to the observed average return” (Chan, 2013, location 665), so his p-value is 1,166 / 10,000, or 0.1166.

**How the draws keep four moments.** The second test’s draws share TU’s first **four moments**, the summary numbers of a distribution.

1. The mean.
2. The standard deviation.
3. The skewness, which measures how lopsided the days are.
4. The **kurtosis**, which measures how much of the variance comes from rare large days.

A normal distribution’s kurtosis is 3, and TU’s is 12.115073. So the null keeps TU’s drift and its fat tails, and drops any pattern in the order of the days (Chan, 2013, location 652).

MATLAB’s `pearsrnd` makes the draws from the **Pearson system**, one family of distributions with a member for nearly any four moments. A number called κ, computed from the skewness and the kurtosis, picks the type, and the four moments then fix the distribution within it. TU’s κ is 0.004645, between 0 and 1, which puts it in type IV. MathWorks does not state which criterion `pearsrnd` applies, so type IV is an inference from the standard criterion in Heinrich (2004), and the draws here follow type IV.

The figure stacks the three nulls on one shared axis. Like everything here it is exploratory.

![Three stacked charts sharing one horizontal axis of mean daily strategy return, from about −1e-4 to 1.5e-4, with a black vertical line at the observed mean of 6.6e-5 in each. The top chart, the first test, shows a dashed brass bell curve centred on 0 that fades out near ±7e-5, and a red outline histogram of the type IV means with the mean set to zero that sits almost on the curve. Its legend gives a one-sided tail of 0.001677 and 19 of 10,000 at or above the line, and labels the red histogram as added after a trial run. The middle chart, the second test, shows a filled brass histogram of the type IV means and a green outline histogram of the normal means, nearly identical, both centred near 3e-5 and spreading from about −5e-5 to 1.2e-4, so the observed line cuts through their right shoulder. Its legend gives 1,221 and 1,165 of 10,000 at or above, and labels the green histogram as added after a trial run. The bottom chart, the third test corrected, shows a narrow brass spike near 2.4e-5, running from about 1e-5 to 4e-5, well left of the observed line, with 0 of 100,000 at or above. The title calls the figure exploratory, and the note names Chan’s file, both seeds, the trial run and the 49 pairs the rule was picked from.](../docs/figures/tu_hypothesis_tests.png)

*The null of each test. The top panel sets the Gaussian null beside the second test’s draws with the drift removed, and the middle panel sets the second test beside a normal draw. The drift-removed draws and the normal draw are both checks added after a trial run. The bottom panel holds the corrected third test alone. Each histogram is a density over the same bins, and the black line is the observed mean.*

## Lesson 1: the Gaussian test lands the script’s 2.93

The script’s comment prints 2.93 for the Gaussian statistic. The run here gives 2.933253, which rounds to it.

```math
t = \frac{\bar r}{s}\,\sqrt{n} = \frac{6.626644\times10^{-5}}{1.010320\times10^{-3}}\,\sqrt{2000} = 2.933253
```

Here r̄ is the observed mean, s is the strategy’s daily standard deviation and n is the 2,000 days. The **spread of the mean**, the standard deviation of an average of n such days, is the daily standard deviation over √n. Read as a test, the statistic counts how many of those spreads the observed mean sits above zero.

```math
\frac{s}{\sqrt{n}} = \frac{1.010320\times10^{-3}}{\sqrt{2000}} = 2.259145\times10^{-5}
```

Under the Gaussian null the mean is normal with that spread and a centre of zero, which is the dashed curve in the figure’s top panel. The chance of a mean at or above 6.626644e-05 is the one-sided tail beyond 2.933253 spreads, 0.001677.

That null assumes three things, and each is a choice.

1. **The days are independent.** Each day’s return tells nothing about the next.
2. **They are normal.** The tails are no fatter than a bell curve’s.
3. **Their true mean is zero.** That rules out drift in the strategy’s own returns.

The second test drops the second assumption and keeps TU’s fat tails. Lesson 5 shows that it drops the third as well, because it keeps TU’s drift.

## Lesson 2: a simulated count lands only within sampling error, so the band comes first

The Gaussian test is arithmetic, so its figure either matches or does not. The second and third tests count random draws, and a different set of draws gives a different count. Each run starts from a **seed**, the number that fixes the random draws so a rerun gives the same ones. A run on another seed than Chan’s, or with another generator, can land only near his count. [The coin-toss post’s Lesson 6](https://github.com/l3a0/quantitative-trading/blob/main/blog/coin-toss-expected-value-vs-growth.md#lesson-6-a-simulation-of-the-coin-can-mislead-in-two-ways) shows a simulated figure moving with its seed.

So the replication wrote down what counts as landing before any draw on the seeds it reports. Call the number of draws N. Each draw either beats the observed mean or does not. If the chance that one draw beats the observed mean is p, the count follows a binomial distribution, the count of successes in N independent tries, and has a standard error of

```math
\text{SE} = \sqrt{N\,p\,(1-p)}
```

The **band** is every count within two standard errors of the printed figure, using the printed proportion as p and the test’s own N. If the true chance equals the printed proportion, about 95 percent of counts fall within two standard errors of it. Chan’s own count is itself one random draw, so a faithful rerun lands inside somewhat less often.

```math
\text{band} = \left[\,\left\lceil Np - 2\,\text{SE}\right\rceil,\ \left\lfloor Np + 2\,\text{SE}\right\rfloor\,\right]
```

That gives three bands.

1. **The book’s 1,166 of 10,000.** The standard error is 32.1, so the band runs from 1,102 to 1,230.
2. **The script’s 0.027500.** At N = 10,000 the standard error is 16.4, so the band runs from 243 to 307.
3. **The book’s 0 of 100,000.** A printed proportion of 0 has a standard error of 0, so only 0 lands.

The written declaration that fixed the bands also fixed the seeds, 20261010 for the second test and 20261011 for the third, and the method that turns each seed into draws. [Entry 37 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-37-three-hypothesis-tests-on-tu-momentum-chans-algorithmic-trading) records the seeds and the bands, written down before any draw on those seeds. A trial run on other seeds had already seen results before that declaration. No count from those seeds is quoted here, because no test in the repository holds them.

Writing the band first matters because a band chosen after the count can always be widened to fit it. [The calendar spreads post’s Lesson 1](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md#lesson-1-a-claim-with-no-number-still-needs-a-pass-mark-written-down-first) makes the same point about a pass mark.

**The result.** On seed 20261010 the second test gives 1,221 of 10,000. That is inside 1,102 to 1,230, nine counts below the top, so the book’s 1,166 **reproduced**, with a gap of +55. The same count, 1,221, is far outside the script’s 243 to 307, so the script’s 0.027500 **did not reproduce**. As a p-value the count is 0.122100, a gap of +0.0946 from the script’s.

**The sampler hits its targets.** Over all 20 million simulated daily returns, the average is 6.014505e-05 against TU’s 5.999783e-05, and the standard deviation is 1.095392e-03 against 1.095464e-03. Both sit within four standard errors of their targets. So the miss on the script’s figure does not come from a sampler that missed TU’s mean or spread.

## Lesson 3: the second test does not give the script’s 0.027500

The book’s count and the script’s comment cannot both come from the second test. One is 0.1166 and the other 0.027500, and the bands around them do not overlap. The second test lands the book and misses the script. What computed the script’s figure stays unknown.

One of the three checks added after the trial run matches the script’s figure. It takes the rule’s actual positions, the ones it held on TU’s real closes, and applies them unchanged to each set of simulated returns. That gives 277 of 10,000, or 0.027700, inside the script’s 243 to 307.

That is a test of a different question. The second test reruns the rule on each simulated price, so the rule chooses new positions every time. The added check keeps one fixed set of bets and asks how those bets would have paid on returns with TU’s moments. Nothing in the script runs it. The file in the published code has one commit, so the history behind the comment is gone, and the match is numerical rather than recovered history. This check came after the trial run, so it carries no verdict.

The habit it teaches is to ask which test printed a figure before comparing it with anything. A p-value in a comment, a caption and a paragraph can come from three different runs.

## Lesson 4: the third test as printed cannot fail

The script writes the third test so that it returns 0 whatever the data. It sets the shuffled positions, `pos_sim`, to zeros. It then adds each shuffle’s trades to `pos`, the rule’s real positions, rather than to `pos_sim`. The return it measures is computed from `pos_sim`, which never changes from zero. So every simulated mean is 0, the observed mean is positive, and no draw can reach it. The run here executes that loop as written for 10 draws, and every simulated return is zero.

A test that cannot fail tells nothing. Here the printed answer happens to survive the fix.

**Corrected.** Building each draw’s positions from its own shuffled signals gives 0 of 100,000 on seed 20261011. The band for the book’s 0 is only 0, so location 672’s “There is not a single sample out of 100,000” **reproduced**. When no draw in N reaches a value, the rule of three puts the p-value below 3/N at 95 percent confidence, so here below 3e-05. The largest shuffled mean is 3.973594e-05 and their average is 2.409664e-05. The observed mean sits 11.131886 standard deviations above that average.

**Why the bottom panel is narrow.** Shuffling scatters the long and short entry days across the sample. So the up to 25 slices held on any day mostly cancel into a net long position, of about the same size on every shuffle. Over the first 500 of those shuffles the net position averages 9.975403 units in absolute size and is long on 0.983958 of days, against 20.58 units and 0.638 of days for the real rule. A position that is nearly the same on every shuffle earns nearly the same mean on the same returns. The shuffled means’ standard deviation is 3.788199e-06, against 2.819219e-05 for the second test’s means on new returns.

**What it rejects.** It rejects the claim that the rule’s timing earns nothing beyond its mix of long and short days. It keeps the real returns, drift included, so the shuffled means average 2.409664e-05 rather than zero. A rule that enters long on 1,274 days and short on 474 holds a net long position on most days, and collects TU’s drift wherever those entries fall.

The habit is to feed a test a case it must fail before trusting a 0.

## Lesson 5: two checks added afterwards point at drift, not kurtosis

Location 674 reads the second test as showing “any random returns distribution with high kurtosis can be favorable to momentum strategies”. Location 2923 repeats it: simulated TU returns with no serial correlation match the strategy “in 12 percent of the random realizations”. Two of the three added checks test that reading by removing one input at a time. Each runs on the same random numbers as the second test, so it differs from that test in the one input alone.

**Removing the fat tails moves the count little.** A normal draw with TU’s mean and standard deviation, and no skewness or excess kurtosis, gives 1,165 of 10,000, against 1,221 for type IV. The middle panel shows the two histograms nearly on top of each other.

**Removing the drift moves it a lot.** Type IV with the mean set to zero gives 19 of 10,000, or 0.001900, close to the Gaussian test’s one-sided 0.001677. The average simulated mean falls from 3.220302e-05 to 3.604899e-07. Those 10,000 means spread with a standard deviation of 2.127120e-05, close to the Gaussian null’s 2.259145e-05. The top panel shows that histogram sitting on the dashed curve. Set against the middle panel, it shows that the drift also widens the type IV means’ spread, from 2.127120e-05 to 2.819219e-05.

**The mechanism is the rule itself.** A series that drifts upward has a positive 250-day return most of the time, so the rule is long most of the time and collects the drift. On the first 1,000 simulated series the rule is long on 0.804654 of signal days, and on 0.502401 once the mean is removed. TU did drift upward, at a mean daily return of 5.999783e-05. Chan’s own Chapter 6 traces TU’s momentum to its roll return, the part of a future’s return that comes from its price converging on the spot price as expiry nears, whose sign rarely changes (Chan, 2013, locations 2326 and 2683).

The book saw this possibility and set it aside. Location 652 names the mean as one way the strategy could be lucky. Location 665 then says it is less likely, “since the position can be long or short at different times”. The checks here say the position is not long or short evenly on a drifting series.

**The status of this finding.** The two checks came after a trial run had seen results, so the drift reading is exploratory. It is a reason to register a test that names drift as the hypothesis before any number exists, and runs it on data Entry 37 never loaded. It is not a verdict that drift explains momentum on TU.

No false-discovery-rate control appears here. Such a control limits the share of false passes across a batch of tests, and it applies when many variants are tried and the best is kept, as [the index arbitrage post’s Lesson 2](https://github.com/l3a0/quantitative-trading/blob/main/blog/index-arbitrage-lessons.md#lesson-2-the-screens-98-is-a-count-of-tests-passed-and-random-walks-unrelated-to-spy-pass-more-often) shows. This replication runs Chan’s three tests and keeps none for a better p-value, and the three added checks carry the exploratory label instead.

**Exploratory.** The drift reading rests on checks chosen after a trial run, and it stays a reason for a registered test rather than a result.

## What this replication cannot say

Four questions are beyond it.

1. **Which Pearson type `pearsrnd` drew from.** Type IV is inferred from the standard criterion rather than read from MathWorks’ code. If `pearsrnd` drew from another type with the same four moments, the second test here judges a different null. The added checks suggest the count barely depends on the shape, which limits what another type could move.
2. **What computed the script’s 0.027500.** One added check lands it with a test the script does not contain, and the file’s history is gone.
3. **Whether drift explains momentum’s significance elsewhere.** The checks ran on one strategy and one future, after a trial run on other seeds. A registered test would declare the drift reading first and run it on data this replication never loaded.
4. **What any of the p-values means once the selection is counted.** The rule came from 49 pairs on the same closes, and nothing here corrects for that.

## What this means for a trader

One habit for each lesson.

1. **Name the null hypothesis before reading a p-value.** A Gaussian null and a moment-matched one give p-values of 0.001677 and 0.122100 for the same strategy.
2. **Fix the seed and the band before the draw.** A simulated count lands only within sampling error, and a band chosen afterwards fits anything.
3. **Check which test printed a figure.** The script’s comment and the book’s paragraph cannot both come from the second test.
4. **Make a test fail once.** A test that returns 0 whatever the data looks exactly like a strong result.
5. **Remove one input at a time before crediting a cause.** Taking out the skewness and excess kurtosis moved the count from 1,221 to 1,165. Taking out the drift took it to 19.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 1.1 and Kindle locations 593, 606, 616, 623, 642, 652, 665, 669, 672, 674, 2326, 2683 and 2923.
2. Chan, E. P. `TU_mom_hypothesisTest.m`, git blob `c0dda16` under `public/img/book2/`, the book’s code, as published at commit `e4bc46f` of [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview).
3. Heinrich, J. (2004). A guide to the Pearson type IV distribution. CDF/MEMO/STATISTICS/PUBLIC/6820.
4. Lo, Mamaysky and Wang (2000), Berntson (2002) and Gill (1999), as *Algorithmic Trading* cites them at locations 623, 606 and 674.

*Not investment advice. Code: [the three tests](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/tu_hypothesis_tests.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/tu_hypothesis_tests_figures.py), with the checks behind [the tests’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_tu_hypothesis_tests.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_tu_hypothesis_tests_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-37-three-hypothesis-tests-on-tu-momentum-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
