# A status page written by hand cost a session turn for every change, and an estimate puts the payback of building it from GitHub at about a day and a third

*Every session that changed this repository’s status page wrote the change by hand, 240 times in 1.9 days, and most reports said the page was still behind. A GitHub Action now rebuilds it, and on an estimate, the move pays back in about a day and a third.*

## An engineering decision rather than a replication

Every other post in this series reproduces a number from one of Ernest Chan’s books. This one reports a decision about how the repository itself runs. Claude Code sessions do the work here, each one an AI coding agent working on one task, and they coordinate through a page called the **build board**. It answers two questions: what is in flight, and what to take next. Each piece of tracked work appears on it as a **card**. Some of what the board shows is **judgement**, meaning what GitHub cannot already say, such as which session holds a card or how the repository’s owner ranks the work.

On 2026-10-11 the board moved. Before, it was a private page hosted on claude.ai, called an artifact, and its data sat in a database attached to that page. Every session that changed something the board showed wrote the change in by hand. After, it is a page on GitHub Pages, GitHub’s hosting for a repository’s static pages. A GitHub Action, a job GitHub runs on its own machines when something happens in the repository, rebuilds it from GitHub whenever an issue, a comment, a pull request or a CI run changes.

The question is what keeping a shared status page true costs when every change is written by hand, and what changed once the page was built from the system that already held the facts.

A session works in turns. A **turn** is one model response and the tools it calls, and the tokens it reads and writes set its price. The dollar figures below value those tokens at list price, and none of them is a bill, because the owner’s subscription charges nothing per token. The dollar serves as a unit that adds up across turns of different sizes. A session can also hand a task to a **sub-agent**, a second Claude instance started for that task that reports back when it finishes.

The answer comes in six lessons.

1. **A page written by hand costs a turn for every change, whatever the change.** 240 updates in 1.9 days used about \$111 a day.
2. **Concurrent writers paid for the version check.** 57 of the 240 updates had a write refused because the board had changed since that session read it.
3. **A hand-written page knows only what some session saw.** 87 of 146 sub-agent transcripts held a report naming something still stale, a count from the transcripts alone.
4. **Judgement kept inside the page could not be read by anything else.** The owner’s ranking had to move onto GitHub before anything could build the page from GitHub.
5. **On an estimate, the move pays back in about a day and a third.** It used \$101.80 of model work and saves an estimated \$77.6 a day.
6. **The move added costs of its own.** Lesson 6 names five, among them 2,903 new lines of script and tests and a page that trails GitHub by a minute or more.

**No test re-derives any measured number in this post.** The cost figures, and the counts of updates, refused writes and reports, come from Claude Code’s transcripts, the logs it keeps of each session. Those are private and stay on one machine, so this public repository cannot commit them. The run counts, run timings, line counts and the count of one-off writes that copied the board’s judgement onto GitHub come from GitHub, and a reader can re-derive them there.

The post states each figure’s window, date and method once, where the figure first appears, and each derived figure shows its arithmetic, so a reader can redo it from the inputs on the page. The “after” figures rest on one example each and carry an estimate label wherever they appear. Unless a sentence gives a later date, every measurement behind a number in this post covers 2026-10-11 or earlier.

## Why a status page has to stay true

A page that says what is in flight is useful only while it is true. A card shown as waiting on review after its pull request merged sends the owner to review finished work. A card shown as free while a session holds it invites a second session to start the same work. So a stale board has a cost, though nothing measured it, and the old way of keeping it current charged for every change in session turns. Lesson 3 counts how often a sub-agent’s report said the board was still behind.

## The board before and after the move

### How sessions kept the board by hand

The procedure lived in a skill, a written set of instructions a session loads and follows. Just before the change that retired it, the skill ran 1,119 lines and named six data sections.

1. The board’s state.
2. The open pull requests.
3. The cards in progress.
4. The planned work.
5. What to take next.
6. The tracker, meaning the repository’s GitHub issues.

A session that changed anything read all six, measured from GitHub what had moved, edited the sections, and ran a harness, a script that rendered the page. The session then read the output against six checks, one of which confirmed that the cards on the page added up to the repository’s open issues. Then it wrote the sections back. Each write carried a version check, a pin that refuses the write when any section it carries has changed since the read. On a refusal the session re-read all six sections, re-ran the harness and wrote again. Most updates went to a sub-agent.

### What the move built

Two changes made the move.

1. The first built the Pages board and its Action, and merged on 2026-10-11 at 19:09:28Z.
2. The second moved the judgement onto GitHub and retired the artifact, and merged at 21:17:12Z.

A script, `scripts/build_board.py`, read GitHub and wrote the six sections as one `board.json` beside the page. The workflow `.github/workflows/board.yml` ran it on six triggers.

1. An issue changes.
2. Anyone comments.
3. A pull request into `main` changes, closed and edited ones included.
4. A run of CI, the repository’s test workflow, finishes.
5. The clock reaches 7 or 37 minutes past the hour. On 2026-10-12 this moved to 8 and 38.
6. Someone starts it by hand.

Three events start no run of their own. Until 2026-10-19 all three reached the board on the next run of any kind.

1. Results from CodeQL, GitHub’s code scanner.
2. “Blocked by” links between issues.
3. Sub-issues.

Since 2026-10-19 the skill tells a session that sets a “blocked by” link or a sub-issue to start a run itself. A link or sub-issue set any other way, such as on GitHub’s web page, still waits for the next run, as CodeQL’s results do.

On 2026-10-29 this repository deleted the script, the page and their tests. The repository’s workflow now calls a shared workflow in the owner’s template repository, pinned to one commit, on the same six triggers, and that workflow runs the template’s own copy of the script and the page.

### Where the judgement went

The judgement became labels, links and lines a session sets on GitHub.

1. `working:build` and `working:decompose` say a session is building or planning a card.
2. A `band:N` label puts a card in priority group N, with band 1 first, and a `Board order:` line in the issue body ranks it within that group.
3. A `decision` label marks a card waiting on the owner.
4. A native “blocked by” link and a `Board after:` line say what it waits on.
5. A `Board verdict:` line in an owner comment says whether its plan is finished.

### What a session does after the move

A session no longer writes the board. It sets a label or a line when it makes a judgement call. Events GitHub already records, such as a pull request merging or CI finishing, reach the board on its next run with nothing set by anyone. The list of three events above names the exceptions. Just after the second change, the skill ran 802 lines, down from 1,119.

![An animated whiteboard sketch titled “The board before and after the move”, drawn slowly stroke by stroke. It is schematic and carries no figures from any run. Two rows of black boxes, joined left to right by black arrows, are read top to bottom. The top row opens on a box marked “session or sub-agent”, under a grey heading “before (by hand)”, and its arrows run on through “read 6 sections + GitHub”, “edit” and “render, 6 checks” to “write + pin”. A vermilion arrow labelled “refused” leaves the bottom of “write + pin”, runs back left beneath the row and rises into “read 6 sections + GitHub”. The bottom row opens on a box marked “session”, under a grey heading “after (from GitHub)”, and its arrows run on through “set label”, “GitHub event” and “Action rebuilds” to “page”. Last, a berry arrow labelled “PR merges / CI finishes” rises from the blank whiteboard below into the bottom of “GitHub event”, with no box behind it. The finished drawing holds for twelve seconds.](../docs/figures/build_board_sketch_update_flow.gif)

*The sketch is schematic. Its boxes follow the order of the steps above, and their sizes and spacing show neither time nor cost. The bottom row shows a label as the example of what a session sets, though a line or a comment starts a run of the Action the same way. The berry arrow stands for the events GitHub records itself, such as a pull request merging or CI finishing. The sketch leaves out the scheduled runs, the runs started by hand and the events that start no run.*

## Lesson 1: a page written by hand costs a turn for every change, whatever the change

### The window and the prices

A cost-measuring procedure kept outside this repository grouped the board-update turns in the transcripts into updates and priced each turn’s tokens at Claude Opus 5.5 list prices. The window runs from 2026-10-10 00:00Z to the second change’s merge at 2026-10-11 21:17Z, which is 1.887 days, and its first update came at 02:44Z. Anthropic’s pricing page, read on 2026-10-11, lists Opus 5.5 at \$4 per million input tokens, \$5 per million written to a five-minute cache, \$8 per million written to a one-hour cache, \$0.20 per million read from cache and \$20 per million output tokens.

### Sub-agent and in-session updates

The window held 240 board updates, and the measurement priced every one. The table’s columns split them into updates made by a board sub-agent and updates made in the session itself.

```math
\small\begin{array}{l|r|r|r}
 & \text{Sub-agent} & \text{Session} & \text{All} \\ \hline
\text{Updates} & 158 & 82 & 240 \\
\text{Median cost, dollars} & 0.92 & 0.33 & 0.81 \\
\text{Median turns} & 14 & 4 &
\end{array}
```

A sub-agent update took a median of 2.0 minutes, and its cost ran from \$0.73 at the 10th percentile to \$1.29 at the 90th. The narrow range fits a fixed cost that every update paid before changing anything. Each one loaded the skill and read all six sections, whatever it had come to change. The measurement did not split the cost to confirm it. A sub-agent also starts with none of its caller’s context, which helps explain why it took 14 turns where an update made in the session itself took 4.

### From turns to dollars a day

The update turns came to \$185.22. Three kinds of turns around them came to \$24.41.

1. 132 turns in which a session started a board sub-agent, \$16.01.
2. 24 turns that only read the board, \$5.73.
3. 28 turns that only loaded the skill or ran the harness, \$2.67.

One run of a set of scripts printed all three. The scripts sat in a session’s scratch folder that no longer exists, but their source survives in that session’s transcript, so reproducing any of the three means recovering the scripts from there and running them again over the same transcripts.

```math
\begin{aligned}
185.22 + 24.41 &= 209.63 \text{ dollars} \\
209.63 / 1.887 &\approx 111.09 \text{ dollars a day} \\
240 / 1.887 &\approx 127.2 \text{ updates a day} \\
209.63 / 240 &\approx 0.87 \text{ dollars an update}
\end{aligned}
```

Reads were most of the update turns’ tokens but under half their dollars. The update turns read 389 million tokens from cache, wrote 17.0 million to it, and produced at least 0.99 million tokens of output. At the prices above, the reads come to about \$78 of the \$185.22, the writes to about \$88, 16.0 million at \$5 a million and 0.94 million at \$8, and the output to about \$20.

The output count is a lower bound, because a transcript can record only part of a reply’s output. So every dollar figure priced from the transcripts can leave out some output, by an amount nothing measured.

## Lesson 2: concurrent writers paid for the version check

The version check did its job. It refused 77 writes, across 57 of the 240 updates, which is 23.75 percent, or about one update in four. Without the check, each of those writes could have overwritten another writer’s change without either writer noticing.

Each refusal cost another full pass: re-read all six sections, re-run the harness and write again. With 77 refusals across 57 updates, 20 of the refusals fell on an update already refused at least once. The measurement did not price the retries apart from the rest of their updates, so their share of the \$209.63 is unknown.

The Action has the same collision and settles it differently. Its runs go one at a time, and when changes arrive faster than runs finish, GitHub keeps only the newest run waiting and cancels the rest. On 2026-10-11, from 19:09Z to 21:35:59Z, the workflow created 274 runs. 128 succeeded, GitHub cancelled 145 while they were still queued, and 1 failed. A cancelled run had started no job, so it used no runner time. A run rebuilds the whole board from GitHub as it stands, rather than from the event that started it. So the next run to start covered everything the cancelled one would have read.

## Lesson 3: a hand-written page knows only what some session saw

A board sub-agent ends its work with a report to the session that started it, and most reports said the board was still behind. Over the same window as Lesson 1, the 158 sub-agent updates left 146 sub-agent transcripts that held a report. The counts differ because a session can resume a sub-agent that has finished and give it another update, and the later round goes into the same transcript. A search for phrases such as “still stale” sorted the transcripts. 87 of the 146 named something still stale, and only 6 said nothing was. The other 53 fell in neither group. That count comes from the transcripts alone, so nothing on GitHub can confirm it.

Two incidents show what a stale card looked like, and both rest on the transcripts alone too.

1. On 2026-10-10 a card most likely sat under “Waiting on your review” after its pull request had merged. The board’s column headings speak in a session’s voice, so that column holds work waiting on the owner, and “Waiting on my review” holds work a session still owes. The transcript that records the incident hedges the claim, and so does this post.
2. On 2026-10-11 the board showed a branch as failing while its checks were green.

Part of the cause is that some events reach no session at all. Two examples are a pull request merged from GitHub’s web page and CI finishing its checks. Nothing told a session that either had happened, so nothing wrote it until some later session looked. Both now start a run of the Action, through the pull request trigger for the merge and the CI trigger for the checks. Not every such event is covered. CodeQL’s results still start no run of their own and wait for the next one.

## Lesson 4: judgement kept inside the page could not be read by anything else

Before the move, the owner’s ranking of the work existed in one place, the artifact’s database. Only a session following the skill could read a card’s priority band, its order within the band and whether its plan was finished. A script reading GitHub could not have built the board, because GitHub did not hold that information.

So the second change had to move it first, through a backfill, a one-off pass that wrote the existing judgement onto GitHub. It planned 60 writes. Of the 8 `working:build` labels planned, the owner allowed only the 4 on cards whose pull requests were still open, so the backfill never wrote the other 4. GitHub’s record shows 53 of the 60 writes landed.

1. 18 of 19 band labels landed.
2. 17 of 18 order lines landed.
3. All 8 decision labels landed.
4. 4 of 8 working labels landed, the 4 the owner allowed.
5. 4 of 5 “blocked by” links landed.
6. Both verdict comments landed.

This post did not trace where the missing band label, order line and link went.

The backfill moved the ranks and left the reasons behind. Each ranked card’s reason and each finished plan’s note was free text the artifact stored for the next session but the page never showed, and the backfill copied none of them onto GitHub. That text survives in the artifact, which is why the owner keeps it, a cost Lesson 6 lists.

## Lesson 5: on an estimate, the move pays back in about a day and a third

### The one-off cost of the move

Building and landing the move used \$101.80 of model work, measured the same way as Lesson 1 over the planning, building and review sessions of 2026-10-11, in five parts.

1. Planning, including the earlier cost measurement, \$6.23.
2. Building the Pages board, \$24.64.
3. Moving the judgement fields, with the backfill, \$29.32.
4. Reviews, \$19.57.
5. The building session’s own thread and other items, \$22.05. The measurement did not separate out some unrelated coordination in this part, so the total runs high by an unmeasured amount.

The measurement rounded each part on its own, so the five sum to \$101.81 rather than \$101.80.

### The estimated daily cost after the move

The estimate rests on two samples, each taken once.

1. One label edit made with `gh issue edit`, from GitHub’s command-line tool, in the session itself rather than in a sub-agent took 2 turns and cost \$0.165, at about 280,000 tokens of context.
2. One board check took 22 turns and cost \$0.92. A board check is the step of a sync round, a session’s periodic pass over what has merged and what to take next, that reads the board, and since the move it builds `board.json` locally. This one ran in a sub-agent, and starting the sub-agent cost a median of \$0.11 over Lesson 1’s window.

The estimate splits the updates two ways. It charges 11.4 percent of them a board check plus the cost of starting it, and the other 88.6 percent one label edit each. The 11.4 percent comes from Lesson 1’s window, where 18 of the 158 sub-agent updates ran a board check for a sync round, and the estimate applies that share to every update. At 127.2 updates a day, the rate Lesson 1 derives:

```math
\begin{aligned}
\text{after} &= 127.2\,[(1-0.114)(0.165) \\
&\qquad + 0.114\,(0.92+0.11)] \\
&\approx 33.53
\end{aligned}
```

That is an estimated \$0.264 per update and about \$33.5 a day.

### The return at three update rates

Four formulas give the move’s return. The cost in each is the \$101.80 the move used.

1. The saving is before minus after.
2. The payback is the cost divided by the saving.
3. The net at N days is the saving times N, minus the cost.
4. The multiple is the net divided by the cost.

For the observed rate, from a before figure of \$111.09 a day and an estimated after figure of \$33.53 a day:

```math
\begin{aligned}
\text{saving} &= 111.09 - 33.53 \\
&= 77.56 \text{ dollars a day} \\
\text{payback} &= 101.80 / 77.56 \approx 1.3 \text{ days} \\
\text{net at 30 days} &= 77.56 \times 30 - 101.80 \\
&= 2{,}225 \text{ dollars} \\
\text{multiple} &= 2{,}225 / 101.80 \approx 22
\end{aligned}
```

The table repeats that arithmetic at half the observed rate and at double it, one rate to a column. In this model every term scales with the update rate, so the saving halves or doubles. That is a simplification, because board checks follow sync rounds rather than updates and the model leaves out the fixed upkeep, meaning the script, its tests and the two defects in Lesson 6.

Only two cells are measured, the observed column’s updates a day and its before cost. The half and double columns scale those two cells, and every row below the line under the before row is an estimate. The daily rows keep cents so that the before, after and saving rows subtract, though the estimate is not precise to the cent. The net row rounds to the dollar.

```math
\small\begin{array}{l|r|r|r}
 & \text{Half} & \text{Observed} & \text{Double} \\ \hline
\text{Updates a day} & 63.6 & 127.2 & 254.4 \\
\text{Before, dollars a day} & 55.55 & 111.09 & 222.18 \\ \hline
\text{After, estimate} & 16.77 & 33.53 & 67.06 \\
\text{Saving, estimate} & 38.78 & 77.56 & 155.12 \\
\text{Payback, days} & 2.6 & 1.3 & 0.7 \\
\text{Net, 30 days} & 1{,}062 & 2{,}225 & 4{,}552 \\
\text{Multiple} & 10 & 22 & 45
\end{array}
```

### Which way the estimate leans

Three known gaps make the computed saving smaller than the true one, two omissions make it larger, and one unknown cuts either way. The three gaps that understate the saving come first.

1. The estimate applies the 11.4 percent to every update. That models 14.5 sync rounds a day, 0.114 × 127.2. Lesson 1’s window measured 9.5 a day, 18 board checks over 1.887 days. At the measured rate, with \$0.165 for each label edit and \$1.03 for each board check and its start, (127.2 − 9.5)(0.165) + 9.5(1.03) gives about \$29.2 a day.
2. It also charges a label edit to updates that now need none, such as a merge.
3. The before figure leaves out the turns that read each sub-agent’s report, which the measurement did not price.

Two omissions overstate the saving.

1. The model leaves out the fixed upkeep. That upkeep has started, and this post prices none of it.
   - Fixes for both defects in Lesson 6 merged on 2026-10-12.
   - Since 2026-10-19 the skill also has a session start a run after setting a “blocked by” link or a sub-issue, a step the estimate does not charge either.
   - On 2026-10-26 the script learned to retry GitHub’s server errors.
2. It charges nothing for loading the skill or reading the board outside an update. Before the move those turns, with the harness runs, cost \$5.73 + \$2.67 = \$8.40, about \$4.45 a day, and nothing measured them after it.

The one unknown is that each of the two samples behind the after figure was taken once, so the after figure could sit high or low by an unknown amount.

### The earlier measurement

An earlier measurement, recorded in one of the repository’s GitHub issues, covered the hand-written board over 2026-10-02 to 2026-10-11. It recorded 642 updates for \$355.79, about \$0.55 an update. They fell on the 7 days that had sessions, about 92 a day, and 108 of them had a write refused, 129 refusals in all. Its finding was that keeping the board current costs “about \$51 a day at Claude Opus 5.5 list prices”.

Its window shares about 1.6 days with this post’s, up to 14:30Z on 2026-10-11, and its method differs. It included only updates that wrote something and left out the `git fetch` and `gh` turns before each one. Its narrower method makes the \$51 low, so the 3.8 days below leans slow.

That \$51 is a cost before the move, so it compares with the before row. It sits near the half-rate column’s \$55.55, but the two match only in that cost. The half-rate column assumes 63.6 updates a day at about \$0.87 each. The earlier measurement found 92 a day at about \$0.55 each. On the earlier measurement’s own inputs, the after estimate is lower and so is the saving.

```math
\begin{aligned}
\text{after} &= 92 \times 0.264 \approx 24.3 \text{ dollars a day} \\
\text{saving} &= 51 - 24.3 = 26.7 \text{ dollars a day} \\
\text{payback} &= 101.80 / 26.7 \approx 3.8 \text{ days}
\end{aligned}
```

That payback of about 3.8 days counts days with sessions, as the \$51 does. On the estimate, it is slower than any column of the table.

## Lesson 6: the move added costs of its own

The board no longer costs a turn for every change, and five costs took the place of that one.

1. **Labels to keep up.** A session still records every judgement call, now as a label or a line rather than an artifact write.
   - Hand-over still needs a step, taking `working:build` off. Before the move that step was a write to the artifact under the version check, and now it is one label edit. Until a session takes `working:build` off, the card stays under “Waiting on my review”, as it did before the move, even once its review and checks are done. On 2026-10-05, six days before the move, the page failed the other way. A rule stopped marking a card as worked on once its pull request opened, so a card a session was still working on showed under “Waiting on your review”. The skill records that defect and its fix.
   - A label edit adds or removes only the labels it names, but a session writes a `Board order:` or `Board after:` line by replacing the whole issue body. GitHub offers no version check on that write, so two writers editing one body, such as two sessions, can lose an edit. Nothing has measured how often.
2. **Two defects found on the day of the move, both fixed the next day, one only in part.**
   - The build failed when someone filed or closed an issue while the script was reading. Its count check could not tell a list cut short from one that changed underneath it. That race caused the one failed run in Lesson 2. On 2026-10-12 the script began reading the whole list again when its count disagreed, for up to three reads in all. Three reads were not always enough, and the race failed two more runs on 2026-10-17. At the commit this repository pins on 2026-11-01, the shared copy still stops after three reads. A run the race fails publishes nothing, so the last good board stays up until a later run succeeds.
   - The script looked for “Part of”, a phrase in a pull request’s description that names the issue it advances, only at the start of a line, so it missed one written mid-paragraph. On 2026-10-11 the owner ruled that the phrase counts anywhere in a description outside code. From 2026-10-12 the script read it there, written with a capital P.
3. **Code.** The move added 2,903 new lines of script and tests. At the second change’s merge, `scripts/build_board.py` was 806 lines and its tests were 1,271. The one-off backfill script and its tests added 394 and 432, so 826 of the new lines served a single pass. The workflow added another 141 lines, outside the 2,903. The page’s own tests, 1,293 lines, were already here and changed with the move. Since 2026-10-29 the script, the page and their tests are not in this repository, and the workflow here is a 112-line file that calls the template’s copy.
4. **Latency and caching.** Over the 128 successful runs in Lesson 2’s window, 19:09Z to 21:35:59Z on 2026-10-11, a run’s two jobs took a median of 36 seconds between them, 19 to build and 17 to deploy. A successful run took a median of 61 seconds from creation to finish, 123 at the 90th percentile and 157 at most. GitHub Pages can then serve an ordinary request for the page’s data from cache for up to 10 minutes. The page itself refetches its data every 2 minutes and bypasses that cache.
5. **A backstop that seldom fired, and a page kept for its notes.**
   - The scheduled runs at 7 and 37 minutes past the hour were the backstop for the events that start no run. As of 22:54Z on 2026-10-11, 3 hours 44 minutes after the first change merged, none had fired, and the first came at 23:06Z. The next day the schedule moved to 8 and 38 minutes past the hour. From that change at 02:30Z on 2026-10-12 to 19:30Z on 2026-10-19, it fired in 41 of 370 slots, about 11 percent, with up to 603 minutes between two scheduled runs. So since 2026-10-19 the skill tells a session that sets a “blocked by” link or a sub-issue to start a run itself, and the schedule stays as a sweep for the rest, such as CodeQL’s results and links set on GitHub’s web page.
   - The owner keeps the retired artifact on claude.ai rather than deleting it, because the artifact is the one place that holds each ranked card’s reason and each plan’s note as they stood when it was retired. Earlier copies survive only in private session transcripts.

GitHub charges nothing for the runs. Its billing page states that Actions usage is free for a public repository on GitHub’s standard hosted runners.

## What this measurement cannot say

Eight limits apply.

1. **What anything cost in money.** Every dollar is usage valued at list price. A subscription charges nothing per token.
2. **Whether 1.9 days is typical.** The before figure comes from 1.887 days that included the move itself. The earlier measurement, which shares about 1.6 of those days and counted differently, found a lower rate and a lower cost per update.
3. **Exactly how many updates the sessions made themselves.** An update inside a session has no clear edges, so a rule joined board turns into one update when only a few other turns separated them. How many turns count as a few is a choice. A cutoff of 4 turns, the one used, gives 82 updates for \$31.43. A cutoff of 2 gives 84 for \$22.96, and a cutoff of 8 gives 74 for \$39.36.
4. **What the move alone cost.** The building session’s \$22.05 includes some unrelated coordination.
5. **What the board cost just after the move.** The after figure rests on one label edit and one board check, with little history behind either, and nothing here prices the board since.
6. **How far the biases go.** The before figure leaves out the turns that read sub-agent reports. The after figure overstates sync rounds and charges a label edit to updates that need none. All three make the computed saving smaller than the true one. Two omissions work the other way: the fixed upkeep, and the skill loads and board reads outside an update. Each of the two samples behind the after figure was also taken once, so it could sit high or low.
7. **Whether the stale reports and the two incidents are accurate.** Those counts come from the transcripts alone, and the transcript that recorded the first incident hedged it.
8. **What a stale label costs a reader.** Nothing measured it, before the move or after.

## References

1. GitHub. GitHub Actions billing. <https://docs.github.com/en/billing/concepts/product-billing/github-actions>, read 2026-10-11.
2. Anthropic. Pricing. <https://platform.claude.com/docs/en/about-claude/pricing>, read 2026-10-11.

*Code as it stood when the move landed: [the script that built the board](https://github.com/l3a0/quantitative-trading/blob/216f8d81cd42a784294eaa1d3e9b773b7f958a2f/scripts/build_board.py), [the workflow that ran it](https://github.com/l3a0/quantitative-trading/blob/216f8d81cd42a784294eaa1d3e9b773b7f958a2f/.github/workflows/board.yml) and [the skill sessions followed](https://github.com/l3a0/quantitative-trading/blob/216f8d81cd42a784294eaa1d3e9b773b7f958a2f/.claude/skills/update-build-board/SKILL.md). Today’s skill is [in the owner’s shared plugin](https://github.com/l3a0/claude-plugins/blob/main/skills/update-build-board/SKILL.md). The code for [the whiteboard sketch](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/build_board_whiteboard.py) sits beside the checks behind [what the sketch draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_build_board_whiteboard.py).*
