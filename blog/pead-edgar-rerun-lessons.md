# Chan’s post-earnings drift moves off his own files, and the 56 stocks EDGAR and a second vendor cannot confirm carry a third of its return

*Chan’s post-earnings drift reproduces to the digit on his own files. Rerun on a calendar built from SEC filings and on another vendor’s prices, the figure moves for four reasons of very different size. The 56 stocks that a check against EDGAR or a check against the second vendor cannot confirm carry a third of the return, and the 13 whose ticker cannot be tied to the right company carry about two thirds of that. The calendar built from filings earns more, mostly by trading more. The vendor barely matters, except at the open.*

## Why rerun a figure that already reproduces

Ernest Chan’s *Algorithmic Trading* trades the morning after an earnings announcement. Call the move from one day’s close to the next day’s open the gap. A stock that announced after the previous close is bought at the open when its gap is at least half its moving deviation, the standard deviation of its gaps over the last 90 days. It is shorted when the gap is at most minus half that deviation. Each position is closed at the same day’s close. The [post on post-earnings drift](https://github.com/l3a0/quantitative-trading/blob/main/blog/post-earnings-drift-lessons.md#the-strategy-and-the-two-files) sets out the rule in full.

The strategy sums each day’s returns across stocks and divides by a fixed 30, whatever the day holds, so every position gets a thirtieth of the capital. Chan reports an APR of 6.7 percent and a Sharpe ratio of 1.5 on the S&P 500 from January 2011 to April 2012 (Chan, 2013, location 3024). His APR is the arithmetic annual return, 252 times the average daily return. The Sharpe ratio is the average daily return over its standard deviation, times the square root of 252, so it measures return per unit of risk. The drift post shows that every figure Chan prints reproduces on the two files he published, one of prices and one of announcement flags.

That reproduction checks his arithmetic on his files. The flag file is the weak one. It holds a 1 for each stock on each day it announced overnight, and nothing records how it was built. The book supplies a function that scraped a year of an earnings calendar from earnings.com, keeping only the announcements made “after the previous trading day’s market close and before today’s market open” (Chan, 2013, location 3002). That calendar cannot be fetched again today. So the drift post’s figures are figures on Chan’s flags, and the question is what happens to them off his files.

A calendar can be rebuilt from public records. A company that releases its earnings files a Form 8-K with the SEC under Item 2.02, “Results of Operations and Financial Condition”. EDGAR, the SEC’s filing system, records the second each filing was accepted. Chan’s stated rule, an announcement between the 4:00 p.m. close and the 9:30 a.m. open Eastern (location 3010), can be read straight off those times.

This repository reran Chan’s rule, his script `pead.m` unchanged, on that calendar and on prices from a second vendor, and split the change in his figure among four differences. It found four things.

1. **A check against EDGAR and a check against a second vendor’s prices drop 56 stocks, and they carry a third of the return.** Chan’s arithmetic annual return of 0.066743 falls to 0.043678 on the 441 stocks that pass both. The 13 whose ticker cannot be tied to the right company carry about two thirds of the drop.
2. **EDGAR’s timestamp needs the filing’s own header.** The time EDGAR’s data service reports is hours late for some filers, which would move a morning filer’s release into the trading session.
3. **The calendar a trader could build earns more, mostly by trading more.** On the same stocks and prices it lifts the return from 0.054481 to 0.071050, and three quarters to four fifths of that comes from the extra trades.
4. **Another vendor’s closes and the price basis barely move the figure, and its opens can.** Three trades on a disputed open move one run more than the vendor and the price basis together.

**Every result here is exploratory.** The comparison was written down before any number on these sources was seen. A check made while planning the rerun had already measured part of the sample, though, and the rule, the window and the divisor of 30 are Chan’s. The rerun can say where the figure moves off his files, and nothing about whether the drift pays today. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rerun and its four differences

Four things can differ from Chan’s files: the stocks, the calendar, the vendor and the price basis. The rerun changes one at a time.

**The stocks.** Chan’s price file holds 497 stocks under their 2012 tickers. A calendar from EDGAR needs each ticker tied to the right filer, and a second vendor’s prices need each ticker tied to the right price series. Each tie has to pass a check, and Lesson 1 says what the checks read. That gives four universes.

1. **ALL**, Chan’s 497 stocks.
2. **CAL**, the 488 whose filer passed its check.
3. **PX**, the 446 whose price series passed its check.
4. **U**, the 441 that pass both.

**The calendar.** Both calendars read the time each filing was accepted, in Eastern time. Several filings on one day make one flag, and an amended filing is skipped.

1. **R1** is the calendar a trader could have built before each open. A filing accepted before 9:30 a.m. on a trading day flags that day. One accepted at 4:00 p.m. or later, or on a day the market was shut, flags the next trading day. One accepted during the session flags nothing, because the gap from the close to the open came before it.
2. **R5** is the calendar nearest Chan’s flags, chosen because it matched them best on a sample of 32 stocks. It differs from R1 in two ways, and each reads what a trader did not have before the open, so no figure on R5 is a tradable one.
   1. A filing accepted during the session flags that same day.
   2. A filing accepted after the date of the event it reports flags the trading day after that event.

**The vendor and the price basis.** The second vendor is Alpha Vantage, whose daily prices for the S&P 500 sit in a private archive, downloaded on 2026-10-05. The vendor’s terms allow personal use only, so the prices stay out of the repository. The adjusted prices, corrected for splits and dividends, are the like-for-like comparison, because Chan’s file is adjusted too. The raw prices are what traded on the day.

Ten runs cover the four differences, each Chan’s rule on one universe, one source of prices and one calendar. **The four on Alpha Vantage prices, C, D, E1 and E5, need the private archive, so a reader cannot rerun them.** The other six read only committed files.

```math
\begin{array}{l|l|l|l|r|r|r}
\text{Run} & \text{Stocks} & \text{Prices} & \text{Flags} & \text{Arithmetic annual return} & \text{Sharpe ratio} & \text{Trades} \\ \hline
\text{A} & \text{ALL} & \text{Chan's} & \text{Chan's} & 0.066743 & 1.4909 & 1{,}072 \\
\text{A\_CAL} & \text{CAL} & \text{Chan's} & \text{Chan's} & 0.054481 & 1.3253 & 1{,}052 \\
\text{A\_PX} & \text{PX} & \text{Chan's} & \text{Chan's} & 0.053099 & 1.5028 & 964 \\
\text{A\_U} & \text{U} & \text{Chan's} & \text{Chan's} & 0.043678 & 1.2815 & 949 \\
\text{B1} & \text{CAL} & \text{Chan's} & \text{R1} & 0.071050 & 1.7045 & 1{,}291 \\
\text{B5} & \text{CAL} & \text{Chan's} & \text{R5} & 0.063142 & 1.2988 & 1{,}477 \\
\text{C} & \text{PX} & \text{adjusted, archive} & \text{Chan's} & 0.053206 & 1.4905 & 964 \\
\text{D} & \text{PX} & \text{raw, archive} & \text{Chan's} & 0.053283 & 1.5255 & 954 \\
\text{E1} & \text{U} & \text{adjusted, archive} & \text{R1} & 0.057489 & 1.6585 & 1{,}172 \\
\text{E5} & \text{U} & \text{adjusted, archive} & \text{R5} & 0.057426 & 1.4118 & 1{,}339
\end{array}
```

Every figure and every difference in this post is rounded from its true value, so a sum or difference of the printed figures can miss by one in the last digit.

A is the drift post’s run, unchanged. Each effect is one run read against another. The universe effect is A_U against A, the calendar’s is B1 against A_CAL, the vendor’s is C against A_PX, and the effect of the price basis is D against C.

Because `pead.m` divides each day by the fixed 30, which the [drift post’s lesson on the 30](https://github.com/l3a0/quantitative-trading/blob/main/blog/post-earnings-drift-lessons.md#lesson-3-the-30-and-the-leverage-are-facts-about-the-run) explains, a run’s arithmetic annual return follows from the trades it takes and their mean return alone, over the 330 days of the window.

```math
\text{arithmetic annual return} = \frac{\text{trades} \times \text{mean return per trade} \times 252}{30 \times 330}
```

A run can raise its return by taking more trades or by earning more on each. The Sharpe ratio does not depend on the 30, because dividing every day by one number scales the mean and the standard deviation alike.

## Lesson 1: EDGAR and a second vendor cannot confirm 56 stocks, and they carry a third of the return

A ticker names a listing, not a company, and tickers get reused. The SEC’s own table of tickers maps today’s symbols, so it sends Chan’s CB to Chubb Limited. In 2012 Chubb Limited was ACE, a different insurer, and it filed its own earnings releases in the window. Its filings are real, from the wrong company. Alpha Vantage files a company under its latest ticker, so its CB series holds ACE’s history too, and Chan’s UTX, United Technologies, sits under RTX.

So each tie has a check that reads only what 2012 recorded.

1. **The filer check, against EDGAR.** A filer passes when four things hold.
   1. It was filing on 2012-03-30.
   2. Its name in EDGAR on that day matches exactly one holding in the iShares S&P 500 fund’s schedule of 2012-03-31.
   3. That holding’s price is within 3 percent of Chan’s close that day.
   4. It released earnings under Item 2.02 in the window.
2. **The price-series check, against the second vendor.** A series passes when it holds a close on every day of the window on which Chan’s file holds one, and its daily returns agree with those of Chan’s closes on all but a few days. Every series of the same company differs on at most 2 days. The four reused tickers that fail, CB among them, differ on 72 to 194. Under Chan’s own tickers, 398 series pass. Searching the archive by returns rather than by ticker finds 48 more, companies filed under a later ticker, which makes PX’s 446.

ACE’s holding sits 5.92 percent above the old Chubb’s close, so ACE’s filer fails the filer check for CB, and the filer that passes is the old Chubb’s.

Nine stocks fail the filer check, in five ways.

1. Five are missing from the fund’s schedule of 2012-03-31, though Chan’s file holds them. Two of those five also carry another company’s filer.
2. Cablevision’s proposed filer is BJ’s Wholesale.
3. DuPont’s is the DuPont formed after 2015, which was not filing on 2012-03-30.
4. NYSE Euronext’s name in EDGAR does not match.
5. Leucadia released nothing under Item 2.02.

The 56 stocks outside U fail for two kinds of reason.

1. **Thirteen cannot be tied to the right company.** They are the nine that fail the filer check and the four reused tickers whose series holds another company’s history.
2. **Forty-three lack the prices to check.** The archive does not hold the company’s prices for the whole window under that ticker. Seven have no series there at all. For 35 the series under that ticker starts after the window ends on 2012-04-24, as ALTR’s starts on 2017-11-01, DELL’s on 2018-12-21 and DOW’s on 2019-03-20. El Paso’s starts on 2011-02-23 and lacks the window’s first 35 days.

Each stock trades on its own gap and its own moving deviation, so dropping some stocks changes nothing about the trades of the rest. A on all 497 is therefore exactly A_U’s trades plus the trades of the 56 stocks outside U. The difference between the two runs is those 56 stocks’ contribution, all of it.

```math
\begin{array}{l|r|r|r}
\text{Stocks} & \text{Count} & \text{Trades} & \text{Contribution to A} \\ \hline
\text{U, both checks pass} & 441 & 949 & 0.043678 \\
\text{fail the filer check} & 9 & 20 & 0.012261 \\
\text{reused ticker, another company's series} & 4 & 8 & 0.002526 \\
\text{no prices for the whole window} & 43 & 95 & 0.008278 \\ \hline
\text{A, all} & 497 & 1{,}072 & 0.066743
\end{array}
```

The 56 stocks outside U take 123 of A’s 1,072 trades and add 0.023065, which is 0.35 of A’s return, about a third. The 13 that cannot be tied to the right company take 28 trades and add 0.014787, which is 0.64 of the 0.023065, about two thirds. The nine that fail the filer check add 0.012261 on their own, which is exactly A against A_CAL.

**This split was measured after the runs, so it is exploratory.** The figure’s top panel builds A’s return day by day from three groups. Its brass line joins the last two rows of the table, the 47 stocks that pass the filer check and have no checked series.

![Two charts. The top chart shows three lines over 330 trading days from January 2011 to April 2012, each the running contribution of one group of stocks to run A’s arithmetic annual return, in percent. All three sit at zero until mid-May. A black line for the 441 stocks of U climbs to under 1 percent by late July, jumps to about 4 percent in early August, dips to about 2.2 percent in November, and ends at 0.043678. A red line for the 9 stocks with no checked filer steps up to about 0.9 percent on a dashed vertical line at 2011-08-04, rises to about 1.6 percent early in 2012, and ends at 0.012261. A brass line for the 47 stocks with a checked filer and no checked series stays near zero until August, steps up at the dashed line, and climbs mostly in 2012 to end at 0.010803. A label at the dashed line says the stocks outside U add 0.010702 on that one day. The bottom chart plots each of six runs as a point, trades taken against mean return per trade. A sits at 1,072 trades and about 0.245 percent, A_CAL at 1,052 and 0.203 percent, A_PX at 964 and 0.216 percent, A_U at 949 and 0.181 percent, B1 at 1,291 and 0.216 percent, and B5 at 1,477 and 0.168 percent. Two dashed curves fall from left to right, each holding the return of A or of A_CAL fixed. Arrows run from A down to A_U, labelled the universe, and from A_CAL to B1 and to B5, labelled R1 and R5. B1 sits above both curves, and B5 between them. The title calls the figure exploratory, and the note says the four runs on the archive’s prices are left out.](../docs/figures/pead_edgar_rerun.png)

*The top panel splits A’s arithmetic annual return among three groups of its stocks. The black line is exactly run A_U, and the other two end on the 0.023065 the universe takes off. The bottom panel is Lesson 3’s evidence. Both panels read only committed files, so the four runs on the archive’s prices are not in the figure.*

The dropped stocks’ return is concentrated. On 2011-08-04, the day A’s cumulative return reaches the high its longest drawdown starts from, the stocks outside U add 0.010702, close to half of their 0.023065, through 8 trades. The largest is a short of MEMC Electronic Materials, Chan’s WFR, which earned 0.1108 from the open to the close. The five largest trades outside U are all shorts, all in the nine stocks that fail the filer check, and they carry 0.54 of the outside sum.

Per trade, the stocks outside U earn 0.007367 on average against 0.001808 inside. Welch’s t, which compares two means without assuming their spreads are equal, is 1.46 (Welch, 1947). That treats every trade as independent, and the trades of one August day are not, so chance cannot be ruled out. The rerun cannot say whether these stocks earn more for a reason or had a few good days.

The universe moves the arithmetic return more than the calendar does, by 0.023065 against 0.016568. The Sharpe ratio ranks them the other way. Dropping the 56 stocks moves it by −0.2094, and R1’s calendar moves it by +0.3792.

## Lesson 2: EDGAR’s timestamp needs the filing’s own header

EDGAR’s data service, the submissions file at `data.sec.gov`, carries an acceptance time marked as UTC. Each filing also has a header file, `.hdr.sgml`, whose acceptance time is Eastern and matches the filing’s own index page.

A check made while planning the rerun compared the two on a sample of 248 filings from 38 filers. In 175 the submissions file was true UTC. In the other 73 it sat a further 4 or 5 hours later, as if the time had been converted from Eastern twice. The extra shift follows the season, 4 hours under daylight saving time and 5 under standard time, and a filer read late was read late on every filing in the sample. Apple was one of them. **That sample is not committed, and nothing in the repository pins its counts.** The index the rerun reads takes every time from the header instead, at the cost of one request per filing.

What a late time does depends on when the filer files.

1. **An evening filer loses nothing.** Each of Apple’s releases in the window was accepted at about 4:30 p.m. Eastern. A double conversion turns the four filed under daylight saving time into about 8:30 p.m., and the two in January, on 2011-01-18 and 2012-01-24, into about 9:30 p.m. All are after the close, so all flag the next morning.
2. **A morning filer loses every release.** No filing in the index was accepted earlier than 06:00:43 Eastern on any day. Read 4 or 5 hours late, every filing accepted between then and 9:30 a.m. lands inside the session, where R1 flags nothing. The index holds 2,930 filings, and 1,460 of them were accepted before the open. Nothing here counts how many of those 1,460 come from filers whose time reads late.
3. **A filer during the session gains a wrong flag.** A filing accepted from 11:00 a.m. onward in winter, or from noon onward in summer, moves past the 4:00 p.m. close and flags the next day, after the gap that should have carried its news. The index holds 405 accepted during the session.

## Lesson 3: the calendar a trader could build earns more, mostly by trading more

The [drift post’s second lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/post-earnings-drift-lessons.md#lesson-2-the-gap-stands-in-for-the-surprise-and-the-flags-stand-in-for-the-calendar) and [its list of open questions](https://github.com/l3a0/quantitative-trading/blob/main/blog/post-earnings-drift-lessons.md#what-this-replication-cannot-say) count how R1’s flags and Chan’s agree, including two of Apple’s releases that his file misses. What matters here is what the difference earns. On CAL’s 488 stocks and Chan’s prices, B1 runs on R1 and A_CAL on Chan’s flags.

```math
\begin{array}{l|r|r|r|r}
\text{Run} & \text{Trades} & \text{Mean return per trade} & \text{Arithmetic annual return} & \text{Sharpe ratio} \\ \hline
\text{A\_CAL, Chan's flags} & 1{,}052 & 0.002035 & 0.054481 & 1.3253 \\
\text{B1, R1} & 1{,}291 & 0.002162 & 0.071050 & 1.7045 \\
\text{B5, R5} & 1{,}477 & 0.001679 & 0.063142 & 1.2988
\end{array}
```

R1 lifts the return by 0.016568 in two ways. It takes 1,291 trades against 1,052, and each earns 0.002162 on average against 0.002035, about 6 percent more. Because the divisor is a fixed 30, more trades at the same mean raise the return in proportion. Priced at Chan’s mean per trade, the extra trades are 0.75 of the gain, three quarters. Priced at R1’s own mean, they are 0.79, nearer four fifths.

The Sharpe ratio rises from 1.3253 to 1.7045, and that gain does not depend on the 30. On this one window R1 earned more per unit of risk, and nothing here tests whether that gap exceeds chance.

On its busiest day B1 holds 49 positions, and on 4 days it holds more than 30. Each position still gets a thirtieth of the capital, so on those days the positions add up to more than the capital, and the strategy borrows the difference.

R5, the calendar nearest Chan’s, gains only by trading more. It takes 1,477 trades at a mean of 0.001679, below Chan’s 0.002035, and its Sharpe ratio sits 0.0265 below A_CAL’s. It holds more than 30 positions on 10 days, and 55 on its busiest. In the figure’s bottom panel, B1 sits up and to the right of A_CAL, above the curve that holds A_CAL’s return fixed. B5 sits down and to the right, and clears that curve only because it takes more trades.

## Lesson 4: another vendor’s closes and the price basis barely move the figure, and its opens can

**Every number in this lesson reads the private archive of Alpha Vantage prices, so a reader cannot rerun it, and every one is exploratory.**

On PX’s 446 stocks with Chan’s flags, switching to Alpha Vantage’s adjusted prices moves the arithmetic annual return by +0.000107, run C against A_PX. Switching from adjusted to raw prices moves it by +0.000078 more, run D against C. Both are about a ten-thousandth.

The price basis barely matters because of how the rerun builds the adjusted open. Alpha Vantage adjusts only the close, so the rerun takes the adjusted open to be the raw open times that day’s adjusted close over its raw close. The same factor then scales both ends of the day, so a trade’s return from the open to the close is the same on either basis. The basis reaches only the overnight gap and its moving deviation, and through them which stocks are traded, 954 in D against 964 in C.

The series check compares closes, and the rule trades from the open. To compare the opens, each archive open is scaled by Chan’s close over the archive’s close that day. After that scaling, 64 of the archive’s opens on PX’s stock-days lie more than 2 percent from Chan’s, across 56 stocks. The 2 percent was chosen after reading the data. Of the 64, 30 fall on 2011-10-27 and 24 on 2011-09-12. Many stocks disagreeing on the same day reads more like two vendors defining the open differently than like 54 separate errors.

Putting Chan’s open in place of each of the 64 moves C by +0.000015 and E1 by −0.000539. It moves E5 by −0.004566 in return and −0.1039 in Sharpe ratio, through three trades.

1. **PNC on 2011-09-12** turns from long to short, worth −0.002261.
2. **MCO on 2012-02-08** stays short and earns less from Chan’s open, worth −0.001751.
3. **TMK on 2011-10-27** stays long and earns less, worth −0.000554.

The PNC flip alone moves E5 more than the vendor and the price basis together. E1’s smaller move is the same MCO and TMK trades plus CAM on 2011-10-27, which turns from long to short and gains 0.001766.

Put together on the 441 stocks of U, the archive’s prices on R1 give E1 an arithmetic annual return of 0.057489 and a Sharpe ratio of 1.6585, above A_U’s 0.043678 and 1.2815. Against Chan’s own figure on all 497, both runs on EDGAR’s calendar come out lower in return, E1 by 0.009254 and E5 by 0.009317. In Sharpe ratio they split. E1 sits 0.1677 above A and E5 0.0790 below.

## What this rerun cannot say

Five questions are beyond it.

1. **Whether the drift pays after 2012.** The window, the rule and the 30 are Chan’s, and a check made while planning the rerun had already looked at the sample. A test that could confirm the drift would fix the rule in writing and run it on later data.
2. **Whether the dropped stocks’ trades were one day’s luck.** Close to half their contribution falls on 2011-08-04, and the t of 1.46 assumes independent trades. More stocks tied to their filers and series, or another window, would be needed to tell.
3. **When each release went out.** A release goes out no later than the filing that reports it is accepted, and can go out earlier. So a filing accepted in the session can follow a release made before the open.
4. **Whether a filing under the earnings item is an earnings release.** Item 2.02 is the item a release is filed under, and nothing here reads the filing’s text, so an 8-K carrying the item for another reason flags a day too.
5. **Whose opens are right where the two vendors disagree.** The two days with dozens of disagreements look like two definitions of the open. Nothing here holds a third source to settle which one a trader could have traded at.

## What this means for a trader

One habit for each lesson.

1. **Tie every ticker to a company at the date of the data, and check the tie.** A lookup by today’s ticker can return real filings or prices from the wrong company. Check too that the vendor holds that company’s prices for the whole window, because a stock with no prices drops out as surely as one tied to the wrong company. The stocks that fail can carry a large share of a backtest’s return.
2. **Read a filing’s time from the filing.** A field labelled UTC can be hours late for some filers, and the error drops a morning filer’s releases from a calendar that trades the open.
3. **Split a return into trades and the mean per trade.** Under a fixed divisor, a calendar that flags more days earns more without trading any better. The Sharpe ratio does not depend on the divisor, so it is the figure to read for that question, though one window cannot settle it.
4. **Check the price a strategy trades at, not only the price it is checked on.** A series that matches on every close can still disagree at the open, and one disputed open can move a figure more than the vendor does.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 7.2 and Kindle locations 3002, 3010 and 3024.
2. `pead.m`, at commit `45670240` of the ivanliu1989/algorithmic_trading mirror of Chan’s code.
3. U.S. Securities and Exchange Commission. EDGAR, the Form 8-K filings under Item 2.02 accepted from 2010-12-01 to 2012-04-24, as recorded on 2026-10-10.
4. Welch, B. L. (1947). The generalization of “Student’s” problem when several different population variances are involved. *Biometrika*, 34, pages 28 to 35.

*Not investment advice. Code: [the rerun](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pead_rerun.py), [the filings record](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/earnings_filings.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pead_rerun_figures.py), with the checks behind [the runs’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pead_rerun.py), [the filings’ counts](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_earnings_filings.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pead_rerun_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-46-post-earnings-drift-on-edgars-calendar-and-the-archives-prices-chans-algorithmic-trading) that records each run and comparison.*
