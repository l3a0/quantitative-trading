---
name: decompose-problem
description: Plan a tracked unit of work to completion by repeatedly auditing its plan against the real code, compacting when it grows, and splitting when compaction stops paying. Use when asked whether a plan is complete, to keep planning an issue, to compress an issue, to decide whether something should be split into sub-tasks, or to reduce work to atomic units before starting it.
---

# Decompose a problem

A plan is a hypothesis about work that has not happened yet. Planning is not writing the
hypothesis down once. It is running passes against reality until a pass stops making the
plan smaller, then deciding whether what is left is one unit of work or several.

## This file is a copy, and the owner's copy wins

The original lives in the owner's `~/.claude/skills/`, where it is used across repositories.
This copy exists because a session spawned into a fresh worktree gets a clean checkout and
nothing outside it, so a skill that is not committed never reaches the sessions that need it.
The price is the one `CLAUDE.md` already names for its copied writing rules: two copies can
drift. The owner's copy is the source, and this one is what gets corrected.

## The loop

Run this against one tracked issue. Each pass is a full cycle.

1. **Audit** the plan against the current code. Findings come from the code, never from
   re-reading the plan.
2. **Apply** what the audit found, to the issue body, so the next reader gets the correction
   rather than the next message.
3. **Record** the pass as a comment: what was found, what it changes, what it was derived
   against. An audit that found nothing is reported and written nowhere, because an issue
   padded with empty notes is harder to read.
4. **Compact** if the body has grown past the band, and verify the compaction mechanically.
5. **Repeat** until a pass does not make the body smaller.
6. **Split** only if the unit is still large when the passes stop paying, and give each child
   the same loop.

**Stop and ask the moment a pass produces a question only the owner can answer.** Do not bank
it for the exit verdict. A ruling changes what the remaining passes are for, so every pass
run before it is a pass spent planning work that may be cut.

## What makes a pass find something

A pass that re-reads the plan finds nothing. Two questions return almost everything, and they
run in this order.

1. **Why is this needed?** Ask it before asking whether the plan is correct, and ask it once,
   at the start. `CLAUDE.md` says reviews armor what exists and rarely ask whether it should.
   A plan can be correct in every detail and describe work with no consumer.
2. **Read what the code already decided in writing.** A docstring stating a rule is a decision
   somebody made on purpose. A plan that contradicts one either loses to it or owes it an
   answer, and a builder meeting it mid-change will either delete it quietly or stop. Grep the
   modules the plan names for their stated rules, and open every signature and every issue the
   plan cites rather than trusting its account of them.

Answer both by measuring rather than reasoning. A plan that cites a number nobody measured is
carrying a guess in a factual voice.

Pin every finding to the commit it was derived against. Line numbers move, and a plan that
cites them without a commit goes stale the next time anything merges.

## Compacting

Compact when the body passes the band, not on a schedule. Cut second tellings, never substance.
The usual candidates, in order of yield:

- a summary of a list that appears in full further down
- a passage re-deriving arithmetic a table already gives
- reasoning that moved to a child issue when a piece was split out
- a moral restating the sentence above it
- a clause saying the same thing as the clause beside it

**Verify every compaction mechanically.** Before and after, diff the sets of backticked
symbols, numbers, issue references, and headings. Anything the diff reports as lost is either
restored or deliberately accounted for. Prose judgment is not enough, because the whole risk
of compacting is losing a fact while the paragraph still reads well.

Two mechanical rules for the edit itself:

1. Assert every match before writing anything, and write the file only after every assertion
   passes. A script that aborts halfway must leave the source untouched.
2. Never push an edit whose script did not complete. Re-fetch the live body and start again.

## Deciding the band

Do not carry a fixed word count. Derive it from what has already shipped in this tracker: pull
the bodies of recently completed issues and take their range. The same for pull request size,
which is what tells you whether a unit is one change or several. A band derived from the
project answers "is this long" in the project's own terms.

## When to stop

**Stop when a pass does not reduce the body.** Compaction counts, a correction that removes
scope counts, an addition does not. It is a bound rather than a judgement: a body over the
band cannot stall, and a pass spent fixing drift the loop itself introduced shrinks nothing so
it ends the loop.

The rule this replaced asked for two consecutive passes finding nothing, which cannot
terminate while the loop edits its own artifact. One run reached 109 passes and never got two
in a row.

Record the stop with the pass count, because a pass count is a cost rather than a depth.

## Splitting

Reach for a split only when the passes have stopped paying and the unit is still large. Size
alone is not a reason, and neither is a section boundary.

**Test each piece for separability.** A piece is separable when both hold:

1. It has its own consumers, ideally more than one, or independent value to someone.
2. It can be built, verified, and merged without the rest.

A piece is welded to the rest when separating it would do any of these:

1. Ship a broken intermediate state, such as a writer without the gate that guards it.
2. Leave code nothing can run, such as a library with no entry point until a later issue.
3. Produce a piece that cannot be verified on its own.

Write the verdict down with the argument, whichever way it goes. "It should not be split, and
here is what is welded to what" is as useful to the next reader as a split would have been, and
it stops the question being reopened every pass.

When a split does happen:

- Use the tracker's own sub-issue mechanism rather than prose references.
- Move the reasoning, not a copy of it. The parent keeps the argument for why the pieces
  belong together, and each child owns its own scope.
- Sweep the parent for sentences that still claim what just left.
- Give each child a milestone, a label, and its dependencies, and state what it blocks.
- Run this loop on each child.

## Atomic

A unit is atomic when a pass no longer reduces it and every remaining piece fails the
separability test. That is the exit condition. Record it on the issue, with the argument, so
the next reader inherits the conclusion rather than the question.

## When work is already running

A correction found after a build session has started must reach that session, not only the
tracker. The session read the issue once, at spawn, and reads none of the conversation that
follows. Send it the finding directly, say plainly whether it changes what they are building,
and say what is deliberately not theirs.

## Scope discipline

Two failures recur, and they pull in opposite directions.

1. **Fixing the instance rather than the class.** One call site corrected while three more
   carry the same mistake.
2. **Fixing past the class.** A correction generalised into places it does not belong, which is
   how a change grows until nothing can review it.

Run both. Completeness checking adds and only over-reach checking removes, so a loop that
runs one lens grows whatever it touches.

When a pass turns up a defect that predates the work, file it separately rather than absorbing
it. Name it on both issues so neither reader loses it. A unit that fixes everything it touched
on the way past is no longer atomic.
