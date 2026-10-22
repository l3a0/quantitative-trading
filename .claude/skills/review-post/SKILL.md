---
name: review-post
description: Review one unpublished blog/*.md post before the owner reads it for publishing, in rounds that loop until nothing significant is left. Full rounds run five independent lenses (accuracy, consistency, easy comprehension, suggested sketch notes, suggested subheadings) and a verifier per lens that tries to refute every finding, then apply what survives on the post's branch and sync its unpublished draft. Once a full round finds only errors in the loop's own edits, later rounds review just the last round's diff and stop when one is clean. Use when asked to review a post before the owner edits or publishes it, to check a post for accuracy, consistency or ease of reading, or to suggest sketch notes or subheadings for a post. Not for reviewing a pull request's code, which CLAUDE.md's `## Pull requests` covers.
---

# Review a post before the owner reads it

The owner reads every unpublished post before publishing it, and one tracking
issue per unpublished post records that pass. A review that lands first lets
the owner read a post that is already right and already easy to follow. The
equity seasonals post took four rounds of review on
[PR #618](https://github.com/l3a0/quantitative-trading/pull/618), assembled
by hand, with the owner picking batches of wording between rounds. On
2026-10-21 the owner asked for the rounds to loop until nothing significant is
left, and then for the loop to decide every change itself.
[Issue 694](https://github.com/l3a0/quantitative-trading/issues/694) records
both rulings.

So the loop never asks the owner mid-loop. It applies every verified finding,
drops a suggestion when the post reads clearer without it, and records each
decision with its reason. The owner reviews the result once, in the pull
request. Publishing, scheduling and any write to a published or scheduled post
still wait for the owner, as `sync-substack` says.

## The loop

Each round has four steps.

1. **Review.** The lenses run at the round's commit, then the round's
   verifiers: one per lens in a full round, one in a diff round.
2. **Decide and apply.** Apply every confirmed or changed finding on the
   post's branch, and drop the rest with a reason. Sync the unpublished draft
   once the round's commits are pushed.
3. **Post the round's comment** on the tracking issue.
4. **Repeat** from the new commit, or stop.

A finding is significant when it is one of three kinds.

1. Any accuracy or consistency finding where some surface states something
   false.
2. A comprehension finding a reader would misread, as the verifier grades it
   below.
3. A display equation or table wider than 320 pixels at the round's commit,
   because a phone reader sees it cut off.

A suggestion an earlier round dropped does not count, and neither does a
cosmetic point, such as a line that wraps short in a docstring.

The rounds run in two phases, by the owner's ruling of 2026-10-21. A loop
review settles the post's original text first, then checks only its own
edits.

1. **Full rounds.** All five lenses read the whole post and everything that
   describes it. The loop leaves this phase after the first full round whose
   significant findings all sit in text the loop itself wrote. That includes
   a README list that an earlier round's rewrite made stale.
2. **Diff rounds.** Each later round reads only the previous round's diff,
   plus every surface that describes a sentence the diff changed: the post's
   own title, summary, alt texts and captions, README's lists, the
   replication log's entry, `data/README.md`, the module docstrings and the
   tests that read the post. Two lenses run, accuracy and consistency, with
   one verifier between them. The comprehension rules apply only to prose
   sentences the diff rewrote, and those two lenses check them. Fixes in this phase are minimal: a
   correction changes only the words that are wrong, and cosmetic points are
   recorded and not applied, since every applied rewrite is new text the next
   round must check.

The loop stops on the first diff round that holds nothing significant. The
diff should shrink each round, since its fixes are minimal. The loop has no cap on its
rounds, because the owner removed a five-round cap on 2026-10-21, and each
round's comment names what the round cost.

The price is that a diff round cannot catch an error in untouched text that
the full rounds missed. In the first run, the pull request's own review found
two errors that three full rounds had read, so that review, under
`## The pull request`, is the backstop. One last full round before hand-over
removes the risk, when the owner asks for that.

The first run, on the commodity seasonals post, predates this rule and ran
eight full rounds. They found 15, 7, 6, 6, 1, 3, 1 and 0 significant findings.
Rounds 1 and 2 found errors that were in the post before the loop began. From
round 3 on, nearly every finding sat in a sentence the round before had just
written, or in a README list that sentence had made stale. Rounds 5 to 8
cost at least 3 to 5 US dollars each and found 1, 3, 1 and 0 significant
findings, nearly all in lines the round before had written. Under
this rule round 3 would have been the last full round.

The comment that ends the loop says it ended and why, with the count of
significant findings in each round, so the owner can see each round adding
less.

## Before round 1

The main thread does seven things before any lens starts, because each lens
reads none of the conversation and needs the answers in its prompt.

1. **Check that the post is unpublished.** Look it up in the drafts,
   scheduled and published lists, as step 2 of `sync-substack`'s
   `## Before any write` gives them. A published or scheduled post gets no
   loop, because every change to it waits on the owner. Run round 1 alone,
   apply nothing, post its findings with each proposed change written out,
   and stop.
2. **Find the tracking issue.** Each unpublished post has one, titled
   "Edit blog/X.md before publishing it on Substack".

   ```bash
   gh issue list --repo l3a0/quantitative-trading --state all \
     --search 'in:title "Edit blog/<post>.md before publishing"' --json number,title,state
   ```

   On 2026-10-21 all 40 such issues were open, and the 8 posts with none were
   mostly published already, so a missing issue is no proof the post is
   unpublished. Step 1 decides that. An unpublished post with no issue gets
   one, in the form of the others: their body, the `documentation` label and
   the milestone of the write-up issue the post came from, as `CLAUDE.md`'s
   `## Pull requests` asks, and `band:3`, as the moment for a filed issue in
   `update-build-board` says.
3. **Mark the card.** Add `working:build` to the tracking issue, as the
   moment for a build session starting on a card in `update-build-board`
   says. The loop pushes to an open pull request for as many rounds as it
   takes, and the label is the only thing on the board saying the branch is still
   moving.
4. **Branch.** Cut the post's branch from `origin/main` in a worktree of its
   own, so the post's commits stay apart from any other work in the session.
   Every commit on it writes `Part of #N` for the tracking issue, and so does
   the pull request, because the issue closes only when the owner publishes.
5. **Read what the owner already decided.** The tracking issue's comments, the
   pull requests that touched the post, and earlier review rounds hold choices
   the owner made, such as a heading picked to pair with another post's. An
   `## Owner decisions` comment, below, lists changes the owner declined.
   Pass all of them to every lens as fixed, so no lens re-proposes them.
6. **Read the live draft, and change nothing.** Run `SYNC.syncTo` without
   `write: true`, from the commit the owner's notes say was last synced to the
   post's last commit, as `sync-substack`'s `### Sync in one call` says. The
   owner's notes are the private records that skill's
   `## This file and the owner's notes` describes. No refusal means the draft
   matches its last sync. A refusal names the check that failed, and it is
   not by itself an owner edit. On the commodity seasonals post it refused on
   two text runs that an earlier patch had split, which the notes recorded.
   Find out why with steps 3 and 4 of `sync-substack`'s
   `## Sync an existing draft`, merging split runs as the paragraph before
   its `### Sync in one call` says, and pull only text the owner changed into the Markdown before the
   lenses read it. A last-synced commit older than the post's last commit
   means the draft lags.
7. **Collect what surrounds the post.** Name the open issues that name it.
   Name the posts that link to it, with the slug sweep under
   `## Decide and apply`, and whether each is published. Name any session
   editing a neighbouring file, so no lens is told to touch it.

Then measure the post's math blocks, as the next section says.

## Before each later round

Write the round's context to one file in the scratchpad, and have every lens
read it first. It names the round's commit, links the earlier rounds'
comments, and lists everything already decided: the owner's choices and every
item an earlier round dropped. A full round asks each lens to check what the
last round rewrote, since a rewrite can bring in a new error. A diff round
gives the lenses the previous round's `git diff` and the surfaces that
describe each changed sentence, and nothing else. Measure the math blocks
again at the round's commit when the diff touched one.

## Measure phone width

`sync-substack`'s `## Check the post before converting it` gives the owner's 320-pixel rule of 2026-10-20 and the measuring method. The main thread
measures, because it needs the one browser, and the result goes straight into
the round's comment rather than to a lens.

The script below reads the draft's own LaTeX, so nothing is pasted. Run it
only once the draft matches the round's commit, because a lagging draft
measures older text. Otherwise put the round's LaTeX, from
`md2substack.py`'s conversion of the commit, in `exprs`. Open a published
post page that holds at least one LaTeX block in the built-in browser, at a
375 by 812 viewport, and fetch the draft from that page, since the API shares
its origin. The draft id is in the owner's notes.

```javascript
const d = await (await fetch('/api/v1/drafts/<draft id>')).json();
const exprs = [];
const walk = (n) => { if (n.type && /latex/i.test(n.type)) exprs.push(n.attrs.persistentExpression || n.attrs.expression); (n.content || []).forEach(walk); };
walk(JSON.parse(d.draft_body));
const host = document.querySelector('[data-component-name="Latex"]');
const widths = [];
for (const e of exprs) {
  const clone = host.cloneNode(false); host.parentNode.appendChild(clone);
  const node = MathJax.tex2chtml(e, { display: true }); node.style.fontSize = '101.8%'; clone.appendChild(node);
  MathJax.startup.document.clear(); MathJax.startup.document.updateDocument();
  widths.push({ w: Math.round(node.querySelector('mjx-math').getBoundingClientRect().width), err: !!node.querySelector('mjx-merror') });
  clone.remove();
}
widths;
```

Measure a candidate fix the same way, with its TeX in `exprs`, before the
round applies it, and measure again after any wording change inside a table.
On the commodity seasonals post all three tables measured 409 to 546 pixels.
Turning one on its side brought it to 302, and the word "streak" in its head
then took it to 319, one pixel under the limit.

## The five lenses

A full round runs all five lenses below. A diff round runs only accuracy and
consistency, scoped to the diff, as `## The loop` says. Each lens runs as its
own background sub-agent, started in one message so all run at once, and none
sees another's prompt or result. Each prompt stands
alone, per the owner's rules for a sub-agent. It names the post, the commit,
the tracking issue, the draft's state, what the owner already decided, the
inbound links, and a scratch folder of the lens's own under the session
scratchpad. It also says what is out of scope: committing to the post's
branch, writing to the draft, or touching any file another session holds.

Four lenses only read, so they can share the post's worktree: accuracy, easy
comprehension, sketch notes and subheadings. The consistency lens writes, so
it runs in a worktree of its own, as below.

Every lens returns each finding in the same form, so its verifier can use it
unchanged.

1. The line number at the round's commit, and the words quoted.
2. What is wrong, in one sentence.
3. The evidence: the command run and what it printed, or the file and line
   read.
4. A proposed change that keeps every fact, written out in full, naming every
   file it touches.

Each lens also returns what it checked and found clean, because the round's
comment reports that too.

1. **Accuracy.** Every number, quotation, page citation, date and claim
   matches its pinned value, its source or the committed data, at the
   precision printed. Recompute what can be recomputed, by calling the post's
   module on the committed data rather than reading a number off a test.
   Check a quotation against `research/book-notes/`, which holds the book's
   highlights by Kindle location, and name any the repository cannot check. A
   claim about what this repository did or did not do is checked against the
   repository, including the open issues collected above. A claim of logic,
   such as "only if", is checked as logic.
2. **Consistency.** The post agrees with README, its entry in
   `docs/replication-log.md`, the module docstrings, the tests, its alt texts
   and its own internal references and headings. Each alt text is checked
   against the figure it describes, by opening the image. Each link resolves
   at the round's commit, anchors included. The posts that link here say
   nothing this post contradicts. This lens also mutates numbers in the post
   and runs the tests, to report which numbers no test holds, so it runs with
   `isolation: "worktree"` and checks out the round's commit first. In
   rounds 1 to 4 of the commodity seasonals post it took 10 to 33 minutes,
   the longest of the five, so the round applies the other lenses' changes while it runs.
3. **Easy comprehension.** It reports:
   - terms used before they are explained
   - ambiguous references, such as "this" or "it" with two candidates
   - sentences that need a second read
   - coined terms, which the writing rules say to replace with what happens
   - the writing-style rules in `CLAUDE.md`, and the rule that a post names
     no issue or pull request, from `sync-substack`'s checklist
   - paragraphs that carry three or more ideas, or put them in an order that
     sends the reader backwards

   It ranks its findings, because it returns the most. Round 1 of the
   commodity seasonals post drew 58.
4. **Suggested sketch notes.** It names the passages where a whiteboard
   sketch would make a rule, bug or statistic easier to follow, what each
   sketch would draw, and the paragraph it would follow. One idea per sketch,
   at most six, and each says whether it carries figures from the run or is
   schematic. From round 2 on it also reviews the sketches already drawn, by
   rendering each GIF's last frame. It draws nothing.
5. **Suggested subheadings.** It proposes a `###` subheading where a section
   runs several ideas together, with the text of each and the line it goes
   above. It names any anchor a renamed `##` heading would break.

## Verify each finding

Each lens's findings go to a verifier of their own as soon as that lens
reports, so verifying overlaps the lenses still running. A diff round sends
both lenses' findings to one verifier. A verifier is a
background sub-agent whose prompt stands alone, like a lens's. In a full
round it sees one lens's findings and nothing else. In a diff round it sees
both lenses' findings and nothing else. It tries to refute each one. It executes
wherever it can: it reruns the command, recomputes the number, opens the
figure, or follows the link. A verifier that writes any file, such as one
rerunning a mutation, runs with `isolation: "worktree"`, because the
read-only lenses still running share the post's worktree.

It checks the proposed text as hard as the finding. On round 1 of the
commodity seasonals post the verifiers caught three wrong rewrites behind
right findings.

1. One credited Chan's own date rolls to the run.
2. One said a file held a row for every trading day, when holidays and gaps
   break that.
3. One sent a Substack reader to a file in the repository.

It returns one verdict per finding.

1. **Confirmed**, with the evidence it reran.
2. **Refuted**, with what shows the finding wrong.
3. **Changed**, where the finding is right but its proposed text is not, with
   the corrected text.

The comprehension verifier also grades each finding, because the stop rule
needs it. In a diff round the one verifier grades the comprehension findings
too. **Misread** means a reader would take a wrong meaning away.
**Reread** means a reader gets it right on a second pass. **Cosmetic** means
the sentence reads right on the first pass and could only read better.

For the two suggestion lenses, the verifier checks the premise rather than the
taste. It checks that the passage is where the line says, that every figure a
sketch would draw is right, that nothing already draws the idea, and that a
heading neither repeats the first sentence under it nor leaves a "that" or
"this" pointing back across it.

A lens's side remark about another lens's ground goes to that lens's verifier.
On round 1 of the commodity seasonals post the sketch lens noticed that Good
Friday 2022 has no row in a natural gas file, which the post's sentence about
holiday rows did not allow, and that became an accuracy fix in three files.

## Decide and apply

Apply every confirmed or changed finding, and drop the rest. Two lenses can
find the same thing. On round 1 of the commodity seasonals post accuracy and
consistency found the same three, so merge overlaps before applying and credit
both.

1. **Accuracy and consistency** are corrections of fact. Fix the class, not
   the instance. On the commodity seasonals post one false claim sat in five
   places: the post, Entry 11, two module docstrings and a figure's note. A
   change to text a figure draws means redrawing the PNG in the same commit
   and updating the test that pins it. A sentence that now states a measured
   fact gets a test that derives it.

   A post's numbers are usually held by no test at all. On the commodity
   seasonals post 26 of 26 single-number mutants of the prose passed every
   test before round 1 added a class that reads the post and checks its
   counts, streaks, gap dates and splits against the run. That class reads one
   copy of each figure, which is the affordable bound. Pinning every second
   copy would have added about 65 assertions, each repeating a derived value.
   Whatever README and the class's docstring say it reads must match what it
   reads, because round 3 and round 4 each found that claim overstated.

   Every change to the post is swept against the surfaces that describe it:
   README's lists of what no test asserts and of facts from outside the data,
   the replication log's entry, and the module docstrings. A sentence that
   gains a number, a fact or a piece of arithmetic changes one of those lists
   in the same commit.

   A fix can reach another post. When that post is unpublished, the fix is
   part of the round: the commit and the pull request write `Part of #M` for
   that post's tracking issue, and the round checks and syncs that post's
   draft too, as step 6 of `## Before round 1` checks this one. When it is
   published or scheduled, its change waits on the owner, and the round's
   comment lists it as dropped for that reason.
2. **Comprehension.** Apply misread and reread findings. In a full round,
   apply a cosmetic one only when the post reads clearer with it. In a diff
   round, record every cosmetic point from either lens and apply none.
3. **Phone width.** Fix every block over 320 pixels with one of the three
   fixes `sync-substack` gives, measured before it is applied.
4. **Sketch notes.** Draw the strongest through `sketch-notes`. Round 1 of
   the commodity seasonals post drew two of five suggestions. The owner's
   ruling on [issue 694](https://github.com/l3a0/quantitative-trading/issues/694)
   changes four of that skill's seven steps, and the sub-agent's prompt says
   so.
   - Step 1's wait for a choice: the round has chosen.
   - Step 3's showing: the pull request does that job, so the sketch is
     placed, tested and committed without waiting.
   - Step 6: the sub-agent opens no pull request and syncs nothing. It
     commits on a branch of its own, and the round merges it, pushes and
     syncs once, uploading the GIFs.
   - Step 7: its review runs before the round merges the sketch, and its
     findings go in the round's comment rather than on the pull request.

   Steps 2, 4 and 5 run as written. A sketch takes its own module and tests,
   so the sub-agent runs with `isolation: "worktree"`.
5. **Subheadings.** Add the confirmed ones. A renamed `##` heading changes
   its anchor, and other posts link anchors by absolute GitHub URL, which
   `test_every_fragment_link_resolves_to_a_heading` skips because the link
   has a scheme. [Issue 586](https://github.com/l3a0/quantitative-trading/issues/586)
   tracks that gap. So sweep for the slug before any rename.

   ```bash
   rg -o '<post>\.md#[a-z0-9-]+' blog/ docs/ README.md
   ```

   Rename only when every post the sweep finds is unpublished, and in the
   same commit update each link and sync each of those drafts. A published
   or scheduled post linking the anchor blocks the rename.

Commit accuracy and consistency each on their own, and the reading changes
(comprehension, subheadings and phone width) together, so the pull request
reads by kind. A sketch arrives as its own merged branch. Name the round in
each commit message. Run the checks each commit needs. Prose needs
`tests/test_markdown_hygiene.py` and `tests/test_substack_converter.py`. A
change to a number, a pinned figure or a test also needs the post's own test
files, which this lists.

```bash
rg -l '<module>|<post>' tests
```

Sync the draft once the round's commits are pushed, per `sync-substack`. A
redrawn figure or a new sketch is a figure uploaded again since the last sync,
so it goes in that skill's `images` argument.

## The round's comment

Post one comment per round on the tracking issue, as
[issue 694](https://github.com/l3a0/quantitative-trading/issues/694) asks. Its
first line is `## Review`, so a later round can find every round by that line.
The build board reads `## Review` only on a pull request, so this comment
moves no card. The comment holds six things, in this order.

1. **What was read.** The round number, the commit, the draft's state and the
   phone widths.
2. **One section per lens.** What it checked, what it found, and what its
   verifier refuted, including when it found nothing.
3. **What was applied**, with the commit for each kind and the reason in one
   line per change.
4. **What was dropped**, with the reason for each. A later round reads this
   list and does not raise a dropped item again unless the text under it
   changed.
5. **The count of significant findings,** and whether the loop goes on.
6. **What the round cost**, priced per `loop-cost` from its agents'
   transcripts.

Link the comment for the owner in chat as soon as it is posted.

## The pull request

Open the post's pull request after round 1's commits are pushed, and send the
owner its link with the tracking issue beside it. Keep pushing later rounds to
it. Its body lists every change by round, with its reason, and every
suggestion dropped, so the owner reviews the whole loop in one place.

Once the loop stops, review the pull request as `CLAUDE.md`'s
`## Pull requests` says. The rounds read the post, and this review reads the
diff, which also holds the tests, docstrings and modules the fixes touched.
So run a completeness lens and an over-reach lens on the diff, and mutate
every test the loop added. Post the review as a comment on the pull request,
whose first line the board reads, and watch the checks until they settle. Then hand it over, and take `working:build` off the tracking issue, as
the moment for a hand-over in `update-build-board` says.

When the owner declines or reverts a change in the pull request, the session
acting on it posts one comment on the tracking issue that opens
`## Owner decisions`. It lists each declined change with the owner's words.
Step 5 of `## Before round 1` reads it as fixed in any later run.

## What it cost

Price the loop per `loop-cost`, counting every agent it ran: each round's
lenses, verifiers and sketch sub-agents, and the pull request's review as a
loop of its own. The main thread's applying, measuring and syncing count only
when its transcript is passed, so say whether they are included. At hand-over,
give one line per round and one for the review in the report to the owner, and
post the same lines as the `## Cost` comment on the tracking issue.
