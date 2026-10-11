# A status page written by hand cost a session turn for every change, and building it from GitHub paid back in about a day and a third

*This repository’s status page was written by hand in every session that changed it, 240 times in 1.9 days, and was still often stale. A GitHub Action now rebuilds it, and on an estimate the move repaid its cost in about a day and a third.*

## An engineering decision rather than a replication

Every other post in this series reproduces a number from one of Ernest Chan’s books. This one reports a decision about how the repository itself runs. The work here is done by Claude Code sessions, each one an AI coding agent working on one task, and those sessions coordinate through a page called the **build board**. It answers two questions: what is in flight, and what to take next.

On 2026-10-11 the board moved. Before, it was a private page hosted on claude.ai, called an artifact, and its data sat in a small database attached to that page. Every session that changed something the board showed wrote the change in by hand. After, it is a page on GitHub Pages, GitHub’s hosting for a repository’s static pages. A GitHub Action, a job GitHub runs on its own machines when something happens in the repository, rebuilds it from GitHub on every change.

The question is what keeping a shared status page true costs when every change is written by hand, and what changed once the page was built from the system that already held the facts. The dollar figures below value model work at list price, and none of them is a bill, because the owner’s subscription charges nothing per token. The answer comes in six lessons.

1. **A page written by hand costs a turn for every change, whatever the change.** 240 updates in 1.9 days used about \$111 a day.
2. **Concurrent writers paid for the version check.** 57 of the 240 updates had a write refused because another session had written first.
3. **A hand-written page knows only what some session saw.** Most board updates ended by reporting something still stale.
4. **Judgement kept inside the page could not be read by anything else.** The owner’s ranking had to move onto GitHub before anything could build the page from GitHub.
5. **The move paid back in about a day and a third, on an estimate.** It used \$101.80 of model work and saves an estimated \$77.59 a day.
6. **The move added costs of its own.** Labels to keep up, two defects already filed, 2,077 new lines of script and tests, and a page that trails GitHub by a minute or more.

**Every figure here is an unpinned measurement.** The cost figures come from Claude Code’s transcripts, the logs it keeps of each session. Those are private and stay on one machine, so this public repository cannot commit them, and no test asserts any figure in this post. Each figure appears once with its window, its date and its method, and each derived figure shows its arithmetic, so a reader can redo it from the inputs on the page. The “after” figures rest on one example each and carry an estimate label wherever they appear.

## Why a status page has to stay true

A page that says what is in flight is useful only while it is true. A card shown as waiting on review after its pull request merged sends the owner to review finished work. A card shown as free while a session holds it invites a second session to start the same work. So the board was worth keeping current, and the old way of keeping it current charged for every change in session turns. A **turn** is one request to the model and its reply, and its price is set by the tokens it reads and writes. Lesson 3 counts how often it was stale anyway.

## The board before and after the move

**Before.** The procedure lived in a skill, a written set of instructions a session loads and follows. Just before the change that retired it, the skill ran 1,119 lines and named six data sections: the board’s state, the open pull requests, the cards in progress, the planned work, what to take next, and the tracker. A session that changed anything read all six, measured from GitHub what had moved, edited the sections, and ran a harness, a script that rendered the page and ran six checks on the output, one of which confirmed that the totals reconcile. Then it wrote the sections back. Each write carried a version pin, a check that refuses the write when another session wrote first. On a refusal the session re-read all six sections, re-ran the harness and wrote again. Most updates were handed to a **sub-agent**, a second Claude instance started for one task that reports back when it finishes.

**The move.** Two changes made it.

1. The first built the Pages board and its Action, and merged on 2026-10-11 at 19:09:28Z. A script, `scripts/build_board.py`, reads GitHub and writes the six sections as one `board.json` beside the page. The workflow `.github/workflows/board.yml` runs it when an issue changes, when anyone comments, when a pull request into `main` changes (closed and edited ones included), when a run of CI, the repository’s test workflow, finishes, at 7 and 37 minutes past every hour, and on a manual start. Three events start no run: results from CodeQL, GitHub’s code scanner, “blocked by” links between issues, and sub-issues. Those reach the board on the next run of any kind.
2. The second moved the judgement onto GitHub and retired the artifact, and merged at 21:17:12Z. Judgement here means what GitHub cannot already say, such as which session holds a card or how the owner ranks the work.

The judgement became five markers a session sets on GitHub.

1. The label `working:build` says a session is building the card.
2. The label `working:decompose` says a session is planning it.
3. A label `band:N` puts a ranked card in a priority band.
4. A `Board order:` line in the issue body orders cards within a band.
5. A `Board verdict:` line in a comment says whether a plan is finished.

**After.** A session no longer writes the board. It sets a marker when it makes a judgement call, and everything GitHub already records, such as a pull request merging or its checks settling, reaches the board with nothing set by anyone. The skill now runs 802 lines.

## Lesson 1: a page written by hand costs a turn for every change, whatever the change

**How the cost was measured.** Every board-update turn was priced from the transcripts at Claude Opus 5.5 list prices. A cost-measuring procedure kept outside this repository grouped the turns into updates and priced each turn’s tokens. The window runs from 2026-10-10 00:00Z to the second change’s merge at 2026-10-11 21:17Z, which is 1.887 days, and its first update came at 02:44Z. Anthropic’s pricing page, read on 2026-10-11, lists Opus 5.5 at \$4 per million input tokens, \$5 per million written to a five-minute cache, \$0.20 per million read from cache and \$20 per million output tokens.

**These dollars are usage valued at list price, not a bill.** The owner’s subscription charges nothing per token. The dollar is used here as a unit that adds up across turns of different sizes, so it measures how much model work the board took.

The window held 240 board updates, and every one was priced.

```math
\begin{array}{l|r|r|r}
\text{Kind of update} & \text{Updates} & \text{Median cost, dollars} & \text{Median turns} \\ \hline
\text{by a board sub-agent} & 158 & 0.92 & 14 \\
\text{in the session itself} & 82 & 0.33 & 4 \\
\text{all} & 240 & 0.81 &
\end{array}
```

A sub-agent update took a median of 2.0 minutes, and its cost ran from \$0.73 at the 10th percentile to \$1.29 at the 90th. The band is narrow because every update paid the same fixed price before it changed anything. It loaded the skill and read all six sections, whatever it had come to change. A sub-agent also starts with none of its caller’s context, which helps explain why it took 14 turns where an update made in the session itself took 4.

The update turns came to \$185.22. Three kinds of turns around them came to \$24.41.

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

By token count, most of that was reading. The turns read 389 million tokens from cache, wrote 17.0 million to it, and produced 1.0 million tokens of output, a count that is a lower bound.

## Lesson 2: concurrent writers paid for the version check

The version pin did its job. It refused 77 writes, across 57 of the 240 updates, which is 23.75 percent, or about one update in four. Without the pin, each of those writes would have overwritten another session’s change without either session noticing.

Each refusal cost a full second pass: re-read all six sections, re-run the harness and write again. The measurement did not price the retries apart from the rest of their updates, so their share of the \$209.63 is unknown.

The Action has the same collision and settles it differently. Its runs deploy one at a time, and when changes arrive faster than runs finish, GitHub keeps only the newest run waiting and cancels the rest. From 19:09Z to 21:35:59Z the workflow created 274 runs. 128 succeeded, 145 were cancelled while still queued, and 1 failed. A cancelled run had started no job, so it used no runner time, and the run after it read everything the cancelled one would have.

## Lesson 3: a hand-written page knows only what some session saw

A sub-agent ended each update with a report, and most reports admitted the board was still behind. Of 146 reports, 87 ended with something still stale and only 6 said nothing was. That count comes from the transcripts alone, so nothing on GitHub can confirm it.

Two incidents show what a stale card looked like, and both rest on the transcripts alone too.

1. On 2026-10-10 a card most likely sat under “Waiting on your review” after its pull request had merged. The source hedged this, and so does this post.
2. On 2026-10-11 the board showed a branch as failing while its checks were green.

One incident can be checked on GitHub. On 2026-10-05 a card sat under “Waiting on your review” while its session was still working, and the current skill records it as a known defect.

Part of the cause is that some events reach no session at all. A pull request merged from GitHub’s web page and a check suite settling are two. Nothing told a session that either had happened, so nothing wrote it until some later session happened to look. Both now start a run of the Action, through the pull request trigger for the merge and the CI trigger for the checks.

## Lesson 4: judgement kept inside the page could not be read by anything else

Before the move, the owner’s ranking of the work existed in one place, the artifact’s database. A card’s band, its order within the band and whether its plan was finished could be read by a session following the skill and by nothing else. A script reading GitHub could not have built the board, because GitHub did not hold that information.

So the second change had to move it first. It planned a backfill, a one-off pass writing the existing judgement onto GitHub, of 60 writes. The owner limited `working:build` to 4 of the 8 cards planned, so about 54 writes landed. Counted at 22:07Z, across issues open and closed, 18 issues carry a `band:N` label and 17 carry a `Board order:` line, against 19 and 18 in the plan. This post did not trace where the missing one of each went.

The backfill moved the ranks and left the reasons behind. Each ranked card’s reason and each plan’s note existed only as free text in the artifact, and they still do, which is why Lesson 6 counts the artifact as kept.

## Lesson 5: the move paid back in about a day and a third, on an estimate

**The cost of the move.** Building and landing the move used \$101.80 of model work, measured the same way as Lesson 1, in five parts.

1. Planning, including the earlier cost measurement, \$6.23.
2. Building the Pages board, \$24.64.
3. Moving the judgement fields, with the backfill, \$29.32.
4. Reviews, \$19.57.
5. The building session’s own thread and small items, \$22.05. This part includes some unrelated coordination, so the total runs slightly high.

Each part is rounded on its own, so the five sum to \$101.81 rather than \$101.80.

**The daily cost after the move, an estimate.** It rests on two samples, each taken once.

1. One label edit made with `gh issue edit` in the calling session took 2 turns and cost \$0.165, at about 280,000 tokens of context.
2. One board check in a sync round, a session’s periodic pass over what has merged and what to take next. The check builds `board.json` locally, and it took 22 turns and cost \$0.92. Starting the sub-agent that runs it cost a measured median of \$0.11.

The estimate charges every update a label edit. It adds a board check, with the cost of starting it, at the share of sub-agent updates that ran one, which was 18 of 158, or 11.4 percent. At 127 updates a day, rounded:

```math
\text{after} = 127\,[(1-0.114)(0.165) + 0.114\,(0.92+0.11)] \approx 33.48
```

That is an estimated \$0.264 per update and \$33.5 a day.

**The estimate is high, and the before figure is low.** Three gaps push the saving down.

1. The estimate applies the 11.4 percent to every update, which models 14.5 sync rounds a day against the 9.5 measured. At the measured rate, (127 − 9.5)(0.165) + 9.5(1.03) gives about \$29.2 a day.
2. It also charges a label edit to updates that now need none, such as a merge.
3. The before figure leaves out the turns that read each sub-agent’s report, which were not priced.

**The return.** Four formulas give it. The cost in each is the \$101.80 the move used.

1. The saving is before minus after.
2. The payback is the cost divided by the saving.
3. The net at N days is the saving times N, minus the cost.
4. The multiple is the net divided by the cost.

For the observed rate, from a before figure of \$111.09 a day and an estimated after figure of \$33.5 a day:

```math
\begin{aligned}
\text{saving} &= 111.09 - 33.50 = 77.59 \text{ dollars a day} \\
\text{payback} &= 101.80 / 77.59 \approx 1.3 \text{ days} \\
\text{net at 30 days} &= 77.59 \times 30 - 101.80 = 2{,}225.90 \text{ dollars} \\
\text{multiple} &= 2{,}225.90 / 101.80 \approx 22
\end{aligned}
```

The table repeats that arithmetic at half the observed rate and at double it. In this model every term scales with the update rate, so the saving halves or doubles. That is a simplification. Board checks follow sync rounds rather than updates, and the fixed upkeep is left out, meaning the script, its tests and the two defects in Lesson 6. Every column after the first two is an estimate. The daily columns keep cents so that each row subtracts exactly, and the net is rounded to the dollar.

```math
\begin{array}{l|r|r|r|r|r|r}
\text{Updates a day} & \text{Before, dollars a day} & \text{After, estimate} & \text{Saving, estimate} & \text{Payback, days} & \text{Net at 30 days, dollars} & \text{Multiple} \\ \hline
\text{63.6, half} & 55.55 & 16.75 & 38.80 & 2.6 & 1{,}062 & 10 \\
\text{127.2, observed} & 111.09 & 33.50 & 77.59 & 1.3 & 2{,}226 & 22 \\
\text{254.4, double} & 222.18 & 67.00 & 155.18 & 0.7 & 4{,}554 & 45
\end{array}
```

**The earlier measurement.** An issue measured the hand-written board once before, over 2026-10-02 to 2026-10-11. It found that keeping the board current costs “about \$51 a day at Claude Opus 5.5 list prices”. It counted 642 updates, about 92 a day over the 7 days that had sessions, for \$355.79 in total, which is about 55¢ an update, and 129 refused writes across 108 updates. That \$51 is a cost before the move, so it compares with the before column, where it sits near the half-rate row’s \$55.55. The two measurements differ in window, in update rate and in cost per update, so the agreement is loose. Read against the earlier figure, the half-rate row is the cautious one, and it still pays back in about 2.6 days, on the estimate.

## Lesson 6: the move added costs of its own

The board no longer costs a turn for every change, and five costs took the place of that one.

1. **Labels to keep up.** A session still sets a marker for every judgement call. A build session must also take `working:build` off when it hands its pull request over, and until it does, its card stays under “Waiting on my review”, the column for work a session still owes.
2. **Two defects already filed.**
   - The build fails when an issue is filed or closed while the script is reading. Its count check cannot tell a list cut short from one that changed underneath it. That race caused the one failed run in Lesson 2.
   - The script reads a pull request’s “Part of” reference only at the start of a line, so it misses one written mid-paragraph. Which form the repository should use is still undecided.
3. **Code.** `scripts/build_board.py` is 806 lines and its tests are 1,271, both new with the move. The page’s own tests, 1,293 lines, were already here and changed with it. The one-off backfill script and its tests add 394 and 432 lines.
4. **Latency and caching.** A run’s job takes a median of 36 seconds, 19 to build and 17 to deploy. A run took a median of 61 seconds from its creation to its finish, 123 at the 90th percentile and 157 at most. GitHub Pages can then serve a plain fetch from cache for up to 10 minutes. The page itself refetches its data every 2 minutes and bypasses that cache.
5. **A backstop not yet seen working, and a page kept for its notes.** The scheduled runs at 7 and 37 minutes past the hour are what catch the events that start no run. As of 22:10Z on 2026-10-11, 3 hours 1 minute after the first change merged, none had fired. The retired artifact is kept rather than deleted, because each ranked card’s reason and each plan’s note live nowhere else.

GitHub charges nothing for the runs. Its billing page states that Actions usage is free for a public repository on GitHub’s standard hosted runners.

## What this measurement cannot say

Eight limits apply.

1. **What anything cost in money.** Every dollar is usage valued at list price. A subscription charges nothing per token.
2. **Whether 1.9 days is typical.** The before figure comes from 1.887 days that included the move itself, and the earlier measurement found a lower rate and a lower cost per update.
3. **Exactly how many updates were made in the sessions themselves.** Turns were grouped into updates by a gap rule. A gap of 4 turns, the one used, gives 82 updates for \$31.43. A gap of 2 gives 84 for \$22.96, and a gap of 8 gives 74 for \$39.36.
4. **What the move alone cost.** The building session’s \$22.05 includes some unrelated coordination.
5. **What the board costs now.** The after figure rests on one label edit and one board check, with little history behind either.
6. **How far the two biases go.** The before figure leaves out the turns that read sub-agent reports, and the after figure overstates sync rounds. Both shrink the saving, and the fixed upkeep the model leaves out works the other way.
7. **Whether the stale reports and the two incidents are accurate.** Those counts come from the transcripts alone, and the first incident was hedged where it was recorded.
8. **What a stale label costs a reader.** Nothing measured it, before the move or after.

## References

1. GitHub. GitHub Actions billing. <https://docs.github.com/en/billing/concepts/product-billing/github-actions>, read 2026-10-11.
2. Anthropic. Pricing. <https://platform.claude.com/docs/en/about-claude/pricing>, read 2026-10-11.

*Code: [the script that builds the board](https://github.com/l3a0/quantitative-trading/blob/main/scripts/build_board.py), [the workflow that runs it](https://github.com/l3a0/quantitative-trading/blob/main/.github/workflows/board.yml), and [the skill sessions follow](https://github.com/l3a0/quantitative-trading/blob/main/.claude/skills/update-build-board/SKILL.md).*
