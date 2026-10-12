# A status page written by hand cost a session turn for every change, and an estimate puts the payback of building it from GitHub at about a day and a third

*Every session that changed this repository’s status page wrote the change by hand, 240 times in 1.9 days, and the page was still often stale. A GitHub Action now rebuilds it, and on an estimate, the move pays back in about a day and a third.*

## An engineering decision rather than a replication

Every other post in this series reproduces a number from one of Ernest Chan’s books. This one reports a decision about how the repository itself runs. Claude Code sessions do the work here, each one an AI coding agent working on one task, and they coordinate through a page called the **build board**. It answers two questions: what is in flight, and what to take next. Each piece of tracked work appears on it as a **card**. Some of what the board shows is **judgement**, meaning what GitHub cannot already say, such as which session holds a card or how the repository’s owner ranks the work.

On 2026-10-11 the board moved. Before, it was a private page hosted on claude.ai, called an artifact, and its data sat in a database attached to that page. Every session that changed something the board showed wrote the change in by hand. After, it is a page on GitHub Pages, GitHub’s hosting for a repository’s static pages. A GitHub Action, a job GitHub runs on its own machines when something happens in the repository, rebuilds it from GitHub on every change.

The question is what keeping a shared status page true costs when every change is written by hand, and what changed once the page was built from the system that already held the facts. A session works in turns. A **turn** is one model response and the tools it calls, and the tokens it reads and writes set its price. The dollar figures below value those tokens at list price, and none of them is a bill, because the owner’s subscription charges nothing per token. The dollar serves as a unit that adds up across turns of different sizes. A session can also hand a task to a **sub-agent**, a second Claude instance started for that task that reports back when it finishes. The answer comes in six lessons.

1. **A page written by hand costs a turn for every change, whatever the change.** 240 updates in 1.9 days used about \$111 a day.
2. **Concurrent writers paid for the version check.** 57 of the 240 updates had a write refused because another session had written first.
3. **A hand-written page knows only what some session saw.** 87 of 146 sub-agent reports ended with something still stale, a count from the transcripts alone.
4. **Judgement kept inside the page could not be read by anything else.** The owner’s ranking had to move onto GitHub before anything could build the page from GitHub.
5. **On an estimate, the move pays back in about a day and a third.** It used \$101.80 of model work and saves an estimated \$77.6 a day.
6. **The move added costs of its own.** Lesson 6 names five, among them 2,903 new lines of script and tests and a page that trails GitHub by a minute or more.

**Every figure here is an unpinned measurement.** The cost figures come from Claude Code’s transcripts, the logs it keeps of each session. Those are private and stay on one machine, so this public repository cannot commit them, and no test asserts any figure in this post. The post states each figure’s window, date and method once, where the figure first appears, and each derived figure shows its arithmetic, so a reader can redo it from the inputs on the page. The “after” figures rest on one example each and carry an estimate label wherever they appear.

## Why a status page has to stay true

A page that says what is in flight is useful only while it is true. A card shown as waiting on review after its pull request merged sends the owner to review finished work. A card shown as free while a session holds it invites a second session to start the same work. So a stale board has a cost, though nothing measured it, and the old way of keeping it current charged for every change in session turns. Lesson 3 counts how often it was stale anyway.

## The board before and after the move

**Before.** The procedure lived in a skill, a written set of instructions a session loads and follows. Just before the change that retired it, the skill ran 1,119 lines and named six data sections.

1. The board’s state.
2. The open pull requests.
3. The cards in progress.
4. The planned work.
5. What to take next.
6. The tracker, meaning the repository’s GitHub issues.

A session that changed anything read all six, measured from GitHub what had moved, edited the sections, and ran a harness, a script that rendered the page. The session then read the output against six checks, one of which confirmed that the totals reconciled. Then it wrote the sections back. Each write carried a version pin, a check that refuses the write when another session wrote first. On a refusal the session re-read all six sections, re-ran the harness and wrote again. Most updates went to a sub-agent.

**The move.** Two changes made it.

1. The first built the Pages board and its Action, and merged on 2026-10-11 at 19:09:28Z.
2. The second moved the judgement onto GitHub and retired the artifact, and merged at 21:17:12Z.

A script, `scripts/build_board.py`, reads GitHub and writes the six sections as one `board.json` beside the page. The workflow `.github/workflows/board.yml` runs it on six triggers.

1. An issue changes.
2. Anyone comments.
3. A pull request into `main` changes, closed and edited ones included.
4. A run of CI, the repository’s test workflow, finishes.
5. The clock reaches 7 or 37 minutes past the hour.
6. Someone starts it by hand.

Three events start no run, and reach the board on the next run of any kind.

1. Results from CodeQL, GitHub’s code scanner.
2. “Blocked by” links between issues.
3. Sub-issues.

The judgement became labels, links and lines a session sets on GitHub.

1. `working:build` and `working:decompose` say a session is building or planning a card.
2. A `band:N` label and a `Board order:` line in the issue body rank it.
3. A `decision` label marks a card waiting on the owner.
4. A native “blocked by” link and a `Board after:` line say what it waits on.
5. A `Board verdict:` line in an owner comment says whether its plan is finished.

**After.** A session no longer writes the board. It sets a label or a line when it makes a judgement call. Events GitHub already records, such as a pull request merging or CI finishing, reach the board on its next run with nothing set by anyone. Lesson 6 names the exceptions. The skill now runs 802 lines.

## Lesson 1: a page written by hand costs a turn for every change, whatever the change

**How the measurement works.** The measurement priced every board-update turn from the transcripts at Claude Opus 5.5 list prices. A cost-measuring procedure kept outside this repository grouped the turns into updates and priced each turn’s tokens. The window runs from 2026-10-10 00:00Z to the second change’s merge at 2026-10-11 21:17Z, which is 1.887 days, and its first update came at 02:44Z. Anthropic’s pricing page, read on 2026-10-11, lists Opus 5.5 at \$4 per million input tokens, \$5 per million written to a five-minute cache, \$8 per million written to a one-hour cache, \$0.20 per million read from cache and \$20 per million output tokens.

The window held 240 board updates, and the measurement priced every one.

```math
\begin{array}{l|r|r|r}
\text{Kind of update} & \text{Updates} & \text{Median cost, dollars} & \text{Median turns} \\ \hline
\text{by a board sub-agent} & 158 & 0.92 & 14 \\
\text{in the session itself} & 82 & 0.33 & 4 \\
\text{all} & 240 & 0.81 &
\end{array}
```

A sub-agent update took a median of 2.0 minutes, and its cost ran from \$0.73 at the 10th percentile to \$1.29 at the 90th. The narrow range fits a fixed price every update paid before it changed anything. It loaded the skill and read all six sections, whatever it had come to change. The measurement did not split the cost to confirm it. A sub-agent also starts with none of its caller’s context, which helps explain why it took 14 turns where an update made in the session itself took 4.

The update turns came to \$185.22. Three kinds of turns around them came to \$24.41. The first part reproduces from the measurement’s scripts. The other two are as the measurement reported them, and no script re-derives them.

1. 132 turns in the calling session that started a board sub-agent, \$16.01.
2. 24 turns that only read the board, \$5.73.
3. 28 turns that only loaded the skill or ran the harness, \$2.67.

```math
\begin{aligned}
185.22 + 24.41 &= 209.63 \text{ dollars} \\
209.63 / 1.887 &\approx 111.09 \text{ dollars a day} \\
240 / 1.887 &\approx 127.2 \text{ updates a day} \\
209.63 / 240 &\approx 0.87 \text{ dollars an update}
\end{aligned}
```

By token count, most of the update turns’ \$185.22 was reading. The update turns read 389 million tokens from cache, wrote 17.0 million to it, and produced at least 1.0 million tokens of output. The output count is a floor because a transcript can record only part of a reply’s output.

## Lesson 2: concurrent writers paid for the version check

The version pin did its job. It refused 77 writes, across 57 of the 240 updates, which is 23.75 percent, or about one update in four. Without the pin, each of those writes could have overwritten another session’s change without either session noticing.

Each refusal cost a full second pass: re-read all six sections, re-run the harness and write again. The measurement did not price the retries apart from the rest of their updates, so their share of the \$209.63 is unknown.

The Action has the same collision and settles it differently. Its runs deploy one at a time, and when changes arrive faster than runs finish, GitHub keeps only the newest run waiting and cancels the rest. From 19:09Z to 21:35:59Z the workflow created 274 runs. 128 succeeded, GitHub cancelled 145 while they were still queued, and 1 failed. A cancelled run had started no job, so it used no runner time, and the run after it read everything the cancelled one would have.

## Lesson 3: a hand-written page knows only what some session saw

A sub-agent ended each update with a report, and most reports said the board was still behind. Over the same window as Lesson 1, 87 of 146 reports ended with something still stale and only 6 said nothing was. That count comes from the transcripts alone, so nothing on GitHub can confirm it.

Two incidents show what a stale card looked like, and both rest on the transcripts alone too.

1. On 2026-10-10 a card most likely sat under “Waiting on your review”, the column for work waiting on the owner, after its pull request had merged. The source hedged this, and so does this post.
2. On 2026-10-11 the board showed a branch as failing while its checks were green.

Part of the cause is that some events reach no session at all. A pull request merged from GitHub’s web page and CI finishing its checks are two. Nothing told a session that either had happened, so nothing wrote it until some later session looked. Both now start a run of the Action, through the pull request trigger for the merge and the CI trigger for the checks. CodeQL’s results still wait for the next run.

## Lesson 4: judgement kept inside the page could not be read by anything else

Before the move, the owner’s ranking of the work existed in one place, the artifact’s database. Only a session following the skill could read a card’s priority band, its order within the band and whether its plan was finished. A script reading GitHub could not have built the board, because GitHub did not hold that information.

So the second change had to move it first. It planned a backfill, a one-off pass writing the existing judgement onto GitHub, of 60 writes. The owner limited `working:build` to the 4 cards whose pull requests were still open, of 8 planned. GitHub’s record shows 53 writes landed: 18 band labels, 17 order lines, 8 decision labels, 4 working labels, 4 “blocked by” links and 2 verdict comments, against 19, 18, 8, 8, 5 and 2 in the plan. This post did not trace where the missing band label, order line and link went.

The backfill moved the ranks and left the reasons behind. Each ranked card’s reason and each plan’s note existed only as free text in the artifact, and they still do, which is why Lesson 6 counts the artifact as kept.

## Lesson 5: on an estimate, the move pays back in about a day and a third

**The cost of the move.** Building and landing the move used \$101.80 of model work, measured the same way as Lesson 1 over the planning, building and review sessions of 2026-10-11, in five parts.

1. Planning, including the earlier cost measurement, \$6.23.
2. Building the Pages board, \$24.64.
3. Moving the judgement fields, with the backfill, \$29.32.
4. Reviews, \$19.57.
5. The building session’s own thread and other items, \$22.05. The measurement did not separate out some unrelated coordination in this part, so the total runs high by an unmeasured amount.

The measurement rounded each part on its own, so the five sum to \$101.81 rather than \$101.80.

**The daily cost after the move, an estimate.** It rests on two samples, each taken once.

1. One label edit made with `gh issue edit` in the calling session took 2 turns and cost \$0.165, at about 280,000 tokens of context.
2. One board check in a sync round, a session’s periodic pass over what has merged and what to take next. The check builds `board.json` locally, and it took 22 turns and cost \$0.92. Starting the sub-agent that runs it cost a median of \$0.11 over Lesson 1’s window.

The estimate charges every update a label edit. It adds a board check, with the cost of starting it, at the share of sub-agent updates that ran one, which was 18 of 158, or 11.4 percent. At 127.2 updates a day, the rate Lesson 1 derives:

```math
\text{after} = 127.2\,[(1-0.114)(0.165) + 0.114\,(0.92+0.11)] \approx 33.53
```

That is an estimated \$0.264 per update and about \$33.5 a day.

**Known biases make the computed saving smaller than the true one, and two unknowns cut either way.** Three gaps understate it.

1. The estimate applies the 11.4 percent to every update, which models 14.5 sync rounds a day against the 9.5 measured. At the measured rate, (127.2 − 9.5)(0.165) + 9.5(1.03) gives about \$29.2 a day.
2. It also charges a label edit to updates that now need none, such as a merge.
3. The before figure leaves out the turns that read each sub-agent’s report, which the measurement did not price.

Against them, the model leaves out the fixed upkeep, which overstates the saving. Each after unit cost is also one sample, so the after figure could sit high or low by an unknown amount.

**The return.** Four formulas give it. The cost in each is the \$101.80 the move used.

1. The saving is before minus after.
2. The payback is the cost divided by the saving.
3. The net at N days is the saving times N, minus the cost.
4. The multiple is the net divided by the cost.

For the observed rate, from a before figure of \$111.09 a day and an estimated after figure of \$33.53 a day:

```math
\begin{aligned}
\text{saving} &= 111.09 - 33.53 = 77.56 \text{ dollars a day} \\
\text{payback} &= 101.80 / 77.56 \approx 1.3 \text{ days} \\
\text{net at 30 days} &= 77.56 \times 30 - 101.80 = 2{,}224.99 \approx 2{,}225 \text{ dollars} \\
\text{multiple} &= 2{,}224.99 / 101.80 \approx 22
\end{aligned}
```

The table repeats that arithmetic at half the observed rate and at double it. In this model every term scales with the update rate, so the saving halves or doubles. That is a simplification. Board checks follow sync rounds rather than updates, and the model leaves out the fixed upkeep, meaning the script, its tests and the two defects in Lesson 6. Every column after the first two is an estimate. The daily columns keep cents so that rows subtract, and the estimate is not precise to the cent. The net column rounds to the dollar.

```math
\begin{array}{l|r|r|r|r|r|r}
\text{Updates a day} & \text{Before, dollars a day} & \text{After, estimate} & \text{Saving, estimate} & \text{Payback, days} & \text{Net at 30 days, dollars} & \text{Multiple} \\ \hline
\text{63.6, half} & 55.55 & 16.77 & 38.78 & 2.6 & 1{,}062 & 10 \\
\text{127.2, observed} & 111.09 & 33.53 & 77.56 & 1.3 & 2{,}225 & 22 \\
\text{254.4, double} & 222.18 & 67.06 & 155.12 & 0.7 & 4{,}552 & 45
\end{array}
```

**The earlier measurement.** An issue measured the hand-written board once before, over 2026-10-02 to 2026-10-11. It found that keeping the board current costs “about \$51 a day at Claude Opus 5.5 list prices”. It counted 642 updates, about 92 a day over the 7 days that had sessions, for \$355.79 in total, which is about \$0.55 an update, and 129 refused writes across 108 updates. That \$51 is a cost before the move, so it compares with the before column. It sits near the half-rate row’s \$55.55, but the match holds only for the before cost. The half-rate row assumes 63.6 updates a day at about \$0.87 each, against the earlier 92 at about \$0.55. On the earlier measurement’s own inputs, the after estimate is lower and so is the saving.

```math
\begin{aligned}
\text{after} &= 92 \times 0.264 \approx 24.3 \text{ dollars a day} \\
\text{saving} &= 51 - 24.3 = 26.7 \text{ dollars a day} \\
\text{payback} &= 101.80 / 26.7 \approx 3.8 \text{ days}
\end{aligned}
```

That payback of about 3.8 days, on the estimate, is slower than any row of the table.

## Lesson 6: the move added costs of its own

The board no longer costs a turn for every change, and five costs took the place of that one.

1. **Labels to keep up.** A session still records every judgement call, now as a label or a line rather than an artifact write. Hand-over still needs a step, taking `working:build` off. Before the move that step was a pinned write to the artifact, and now it is one label edit. Until it happens, the card stays under “Waiting on my review”, the column for work a session still owes, as it did before the move. On 2026-10-05 a page rule that dropped the entry too early had the opposite effect. It put a working card under “Waiting on your review”, and the skill records that defect and its fix.
2. **Two defects already filed.**
   - The build fails when someone files or closes an issue while the script is reading. Its count check cannot tell a list cut short from one that changed underneath it. That race caused the one failed run in Lesson 2.
   - The script reads “Part of”, a line in a pull request’s description naming the issue it advances, only at the start of a line, so it misses one written mid-paragraph. Which form the repository should use is still undecided.
3. **Code.** The move added 2,903 new lines of script and tests. `scripts/build_board.py` is 806 lines and its tests are 1,271. The one-off backfill script and its tests add 394 and 432, so 826 of the new lines served a single pass. The workflow is 141 lines. The page’s own tests, 1,293 lines, were already here and changed with the move.
4. **Latency and caching.** A run’s two jobs take a median of 36 seconds between them, 19 to build and 17 to deploy. A successful run took a median of 61 seconds from creation to finish, 123 at the 90th percentile and 157 at most. GitHub Pages can then serve a plain fetch from cache for up to 10 minutes. The page itself refetches its data every 2 minutes and bypasses that cache.
5. **A backstop not yet seen working, and a page kept for its notes.** The scheduled runs at 7 and 37 minutes past the hour are what catch the events that start no run. As of 22:54Z on 2026-10-11, 3 hours 44 minutes after the first change merged, none had fired. The repository keeps the retired artifact rather than deleting it, because each ranked card’s reason and each plan’s note live nowhere else.

GitHub charges nothing for the runs. Its billing page states that Actions usage is free for a public repository on GitHub’s standard hosted runners.

## What this measurement cannot say

Eight limits apply.

1. **What anything cost in money.** Every dollar is usage valued at list price. A subscription charges nothing per token.
2. **Whether 1.9 days is typical.** The before figure comes from 1.887 days that included the move itself, and the earlier measurement found a lower rate and a lower cost per update.
3. **Exactly how many updates the sessions made themselves.** An update inside a session has no clear edges, so a rule joined board turns into one update when only a few other turns separated them. The cutoff is a choice. A cutoff of 4 turns, the one used, gives 82 updates for \$31.43. A cutoff of 2 gives 84 for \$22.96, and a cutoff of 8 gives 74 for \$39.36.
4. **What the move alone cost.** The building session’s \$22.05 includes some unrelated coordination.
5. **What the board costs now.** The after figure rests on one label edit and one board check, with little history behind either.
6. **How far the biases go.** The before figure leaves out the turns that read sub-agent reports, and the after figure overstates sync rounds. Both make the computed saving smaller than the true one. The fixed upkeep the model leaves out works the other way, and each after unit cost is a single sample that could sit high or low.
7. **Whether the stale reports and the two incidents are accurate.** Those counts come from the transcripts alone, and the source that recorded the first incident hedged it.
8. **What a stale label costs a reader.** Nothing measured it, before the move or after.

## References

1. GitHub. GitHub Actions billing. <https://docs.github.com/en/billing/concepts/product-billing/github-actions>, read 2026-10-11.
2. Anthropic. Pricing. <https://platform.claude.com/docs/en/about-claude/pricing>, read 2026-10-11.

*Code: [the script that builds the board](https://github.com/l3a0/quantitative-trading/blob/main/scripts/build_board.py), [the workflow that runs it](https://github.com/l3a0/quantitative-trading/blob/main/.github/workflows/board.yml), and [the skill sessions follow](https://github.com/l3a0/quantitative-trading/blob/main/.claude/skills/update-build-board/SKILL.md).*
