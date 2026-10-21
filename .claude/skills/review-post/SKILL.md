---
name: review-post
description: Review one blog/*.md post before the owner reads it for publishing, in rounds that loop until nothing significant is left. Each round runs five independent lenses (accuracy, consistency, easy comprehension, suggested sketch notes, suggested subheadings) and a verifier per lens that tries to refute every finding, then applies what survives on the post's branch, syncs its unpublished draft and re-reviews. Use when asked to review a post before the owner edits or publishes it, to check a post for accuracy, consistency or ease of reading, or to suggest sketch notes or subheadings for a post. Not for reviewing a pull request's code, which CLAUDE.md's `## Pull requests` covers.
---

# Review a post before the owner reads it

The owner reads every unpublished post before publishing it, and one tracking
issue per post records that pass. A review that lands first lets the owner
read a post that is already right and already easy to follow. The equity
seasonals post took four rounds of review on
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

1. **Review.** The five lenses run at the round's commit, then a verifier per
   lens.
2. **Decide and apply.** Apply every confirmed or changed finding on the
   post's branch, and drop the rest with a reason. Sync the unpublished draft
   once the round's commits are pushed.
3. **Post the round's comment** on the tracking issue.
4. **Repeat** from the new commit, or stop.

The loop stops on the first round whose verified findings hold nothing
significant. A finding is significant when it is any accuracy or consistency
finding, or a comprehension finding a reader would misread rather than merely
reread. A suggestion an earlier round dropped does not count, and neither does
a cosmetic point. The loop also stops after five rounds, even if the last one
still found something, so a lens that never runs dry cannot keep it going.

The comment that ends the loop says it ended and why, with the count of
findings in each round, so the owner can see each round adding less.

## Before round 1

The main thread does six things before any lens starts, because each lens
reads none of the conversation and needs the answers in its prompt.

1. **Find the tracking issue.** Each unpublished post has one, titled
   "Edit blog/X.md before publishing it on Substack".

   ```bash
   gh issue list --repo l3a0/quantitative-trading --state all \
     --search 'in:title "Edit blog/<post>.md before publishing"' --json number,title,state
   ```

   A closed one means the post is published, so every change waits on the
   owner and the loop does not apply anything. Where none exists, file one in
   the form of the others, with their body, the `documentation` label,
   `band:3`, and the milestone of the write-up issue the post came from.
2. **Branch.** Cut the post's branch from `origin/main` in a worktree of its
   own, so the post's commits stay apart from any other work in the session.
   Every commit on it writes `Part of #N` for the tracking issue, and so does
   the pull request, because the issue closes only when the owner publishes.
3. **Read what the owner already decided.** The tracking issue's comments, the
   pull requests that touched the post, and earlier review rounds hold choices
   the owner made, such as a heading picked to pair with another post's. Pass
   them to every lens as fixed, so no lens re-proposes them.
4. **Read the live draft, and change nothing.** Compare its
   `draft_updated_at` and the hash of its raw `draft_body` with the baseline
   in the owner's notes. Equal means no edits by the owner since the last
   sync, which is the usual case and costs one read. A draft that differs
   holds edits the owner made in the Substack editor, and those are part of
   the post. Find them with step 3 of `sync-substack`'s
   `## Sync an existing draft`, and pull them into the Markdown before the
   lenses read it. Check too whether the draft lags the Markdown, by comparing
   the commit it was last synced to with the post's last commit.
5. **Measure every math block's width on a phone,** as below.
6. **Collect what surrounds the post.** Name the open issues that name it.
   Name the posts that link to it, by file and by anchor, and when each
   publishes. Name any session editing a neighbouring file, so no lens is
   told to touch it.

## Before each later round

Write the round's context to one file in the scratchpad, and have every lens
read it first. It names the round's commit, links the earlier rounds'
comments, and lists everything already decided: the owner's choices and every
item an earlier round dropped. A later round reviews the post as it now
stands, so it also asks each lens to check what the last round rewrote, since
a rewrite can bring in a new error. The four read-only lenses can share the
post's worktree, as long as nothing writes to it while they run.

## Measure phone width

The owner's rule of 2026-10-20 keeps each display equation and table at or
under 320 pixels, and `sync-substack`'s `## Check the post before converting
it` gives the rule and the measuring method. The main thread measures, because
it needs the one browser, and the result goes straight into the round's
comment rather than to a lens.

The draft's own LaTeX can be measured without pasting it. Open any published
post page in the built-in browser at a 375 by 812 viewport, then fetch the
draft from that page, since the API shares its origin.

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

Each lens runs as its own background sub-agent, started in one message so all
five run at once, and none sees another's prompt or result. Each prompt stands
alone, per the owner's rules for a sub-agent. It names the post, the commit,
the tracking issue, the draft's state, what the owner already decided, the
inbound links, and a scratch folder of the lens's own under the session
scratchpad. It also says what is out of scope: editing the post, the draft, or
any file another session holds.

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
   repository, including the open issues collected above.
2. **Consistency.** The post agrees with README, its entry in
   `docs/replication-log.md`, the module docstrings, the tests, its alt texts
   and its own internal references and headings. Each alt text is checked
   against the figure it describes, by opening the image. Each link resolves
   at the round's commit, anchors included. The posts that link here say
   nothing this post contradicts. This lens also mutates numbers in the post
   and runs the tests, to report which numbers no test holds, so it runs with
   `isolation: "worktree"`. It is the slowest lens, at about 15 minutes on
   the commodity seasonals post against 2 to 7 for the others.
3. **Easy comprehension.** It reports:
   - terms used before they are explained
   - ambiguous references, such as "this" or "it" with two candidates
   - sentences that need a second read
   - coined terms, which the writing rules say to replace with what happens
   - the writing-style rules in `CLAUDE.md`, and the rule that a post names
     no issue or pull request, from `sync-substack`'s checklist
   - paragraphs that carry three or more ideas, or put them in an order that
     sends the reader backwards

   It ranks its findings, because it returns the most. The commodity
   seasonals post drew 58.
4. **Suggested sketch notes.** It names the passages where a whiteboard
   sketch would make a rule, bug or statistic easier to follow, what each
   sketch would draw, and the paragraph it would follow. One idea per sketch,
   at most six, and each says whether it carries figures from the run or is
   schematic. It draws nothing.
5. **Suggested subheadings.** It proposes a `###` subheading where a section
   runs several ideas together, with the text of each and the line it goes
   above. It names any anchor a renamed `##` heading would break.

## Verify each finding

Each lens's findings go to a verifier of their own as soon as that lens
reports, so verifying overlaps the lenses still running. A verifier sees one
lens's findings and nothing else, and tries to refute each one. It executes
wherever it can: it reruns the command, recomputes the number, opens the
figure, or follows the link. It checks the proposed text as hard as the
finding, because on the commodity seasonals post the verifiers caught three
wrong rewrites behind right findings. One credited Chan's own date rolls to
the run, one said a file held a row for every trading day when holidays and
gaps break that, and one sent a Substack reader to a file in the repository.

It returns one verdict per finding.

1. **Confirmed**, with the evidence it reran.
2. **Refuted**, with what shows the finding wrong.
3. **Changed**, where the finding is right but its proposed text is not, with
   the corrected text.

The comprehension verifier also grades each finding, because the stop rule
needs it: **misread**, where a reader would take a wrong meaning away,
**reread**, or **cosmetic**.

For the two suggestion lenses, the verifier checks the premise rather than the
taste. It checks that the passage is where the line says, that every figure a
sketch would draw is right, that nothing already draws the idea, and that a
heading neither repeats the first sentence under it nor leaves a "that" or
"this" pointing back across it.

A lens's side remark about another lens's ground goes to that lens's verifier.
On the commodity seasonals post the sketch lens noticed that Good Friday has
no row in the natural gas files, and that became an accuracy fix in three
files.

## Decide and apply

Apply every confirmed or changed finding, and drop the rest. Two lenses often
find the same thing. On the commodity seasonals post accuracy and consistency
both found three, so merge them before applying and credit both.

1. **Accuracy and consistency** are corrections of fact. Fix the class, not
   the instance: a false claim usually sits in the post, the replication log,
   a module docstring and a figure's note at once. A change to text a figure
   draws means redrawing the PNG in the same commit and updating the test
   that pins it, and a sentence that now states a measured fact gets a test
   that derives it.
2. **Comprehension.** Apply misread and reread findings. Apply a cosmetic one
   only when the post reads clearer with it, and drop it otherwise.
3. **Sketch notes.** Draw the strongest, usually two or three, through
   `sketch-notes`. That skill's step 3 shows each sketch to the owner before
   it is placed. In this loop the pull request does that job, by the owner's
   ruling on [issue 694](https://github.com/l3a0/quantitative-trading/issues/694),
   so the sketch is placed, tested and committed without waiting. A sketch
   takes its own module and tests, so it suits a sub-agent with
   `isolation: "worktree"` that commits on a branch of its own, which the
   round then merges.
4. **Subheadings.** Add the confirmed ones. Leave a `##` heading's text
   alone unless the gain is large, because another post may link its anchor
   by an absolute GitHub URL, and no test checks one of those.
   `test_every_fragment_link_resolves_to_a_heading` skips any link with a
   scheme, which [issue 586](https://github.com/l3a0/quantitative-trading/issues/586)
   tracks. Until it closes, sweep for the slug instead.

   ```bash
   rg -o '<post>\.md#[a-z0-9-]+' blog/ docs/ README.md
   ```

Commit each lens's changes on their own, so the pull request reads by kind,
and name the round in each commit message. Run the checks each commit needs:
`tests/test_markdown_hygiene.py` and the converter test for prose, and the
post's own test files whenever a number, a pinned figure or a test changes.

Sync the draft once the round's commits are pushed, per `sync-substack`. A
redrawn figure or a new sketch is a figure uploaded again since the last sync,
so it goes in that skill's `images` argument.

## The round's comment

Post one comment per round on the tracking issue. Its first line is
`## Review`, so the build board reads it as a review. It holds five things, in
this order.

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

Link the comment for the owner in chat as soon as it is posted.

## The pull request

Open the post's pull request after round 1's commits are pushed, and keep
pushing later rounds to it. Its body lists every change by round, with its
reason, and every suggestion dropped, so the owner reviews the whole loop in
one place. Review it as `CLAUDE.md`'s `## Pull requests` says, and watch its
checks.

## What it cost

Price each round's lenses and verifiers per `loop-cost` once the round's last
verifier reports, and post the `## Cost` comment on the tracking issue when the
loop ends, with one line per round.
