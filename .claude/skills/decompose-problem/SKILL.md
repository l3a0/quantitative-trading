---
name: decompose-problem
description: Plan a tracked unit of work to completion by repeatedly auditing its plan against the real code, compacting when it grows, and splitting when compaction stops paying. Use when asked whether a plan is complete, to keep planning an issue, to compress an issue, to decide whether something should be split into sub-tasks, or to reduce work to atomic units before starting it.
---

# Decompose a problem

A plan is a hypothesis about work that has not happened yet. Planning is not writing the
hypothesis down once. It is running passes against reality until the passes stop finding
anything, then deciding whether what is left is one unit of work or several.

## This file is a copy, and the owner's copy wins

The original lives in the owner's `~/.claude/skills/`, where it is used across repositories.
This copy exists because a session spawned into a fresh worktree gets a clean checkout and
nothing outside it, so a skill that is not committed never reaches the sessions that most
need it. Five loops ran against this repo's issues that way.

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
5. **Repeat** until two consecutive passes, asking different questions, return nothing.
6. **Split** only if the unit is still large when the passes stop paying, and give each child
   the same loop.

## What makes a pass find something

A pass that re-reads the plan finds nothing. These are the questions that return findings.
They are ordered by how often they have paid.

1. **Read what the code already decided in writing.** A docstring stating a rule is a decision
   somebody made on purpose. A plan that contradicts one either loses to it or owes it an
   answer, and a builder meeting it mid-change will either delete it quietly or stop. Grep the
   modules the plan names for their stated rules before trusting the plan's account of them.
2. **Open every signature the plan names.** Plans routinely describe a function by what it
   does and get its arguments wrong. "It takes a path, not a root" is a small correction that
   saves a builder an hour.
3. **Measure instead of assuming.** List the directory. Read the row counts. Query the real
   data. A plan that cites a number nobody measured is carrying a guess in a factual voice.
4. **Ask what the second run does.** Idempotence is where plans break. Run it twice, run it
   with a different argument, run it after a partial failure. Two of the sharpest findings in
   the session this skill came from were "this appends every night forever" and "re-running
   with a corrected value corrupts the record".
5. **Ask where the error surfaces**, not just that it is raised. An exception that reaches an
   operator as a stack trace is a weaker guard than one that prints a line, and plans specify
   the raise while forgetting the reader.
6. **Look for the document contradicting itself.** After a split or an edit, one section
   claims what another section gave away. Sweep for the class, not the instance.
7. **Ask whether a new capability makes an unreachable failure reachable.** A guard that was
   never needed becomes owed the moment an option lets two runs disagree.

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

## Diminishing returns, judged against yourself

Stop when the character of the findings changes, not when their count drops. A pass is still
paying while it returns defects: a contract the plan got wrong, a failure mode nobody named, a
decision the code already made. A pass has stopped paying when it returns only restatement,
reassurance that something is fine, or style.

**Predicting that the next pass will find nothing is not evidence.** Only a pass that ran and
found nothing is. The prediction comes from the same reading that produced the plan, so it
inherits that reading's blind spots, and it is reliably wrong. In the session this skill came
from, a unit was called complete and handed to a builder, and the next pass found that every
refusal in the command reached the operator as a stack trace rather than a line. The pass
before that one had found the epoch measured from the wrong surface entirely. Each was called
the last one at the time.

So require **two consecutive passes that find nothing**, and make the second ask different
questions from the first. A pass returning nothing while re-asking what the previous pass
already asked is not a second data point, it is the same one. Work down the question list
above and then reach past it: the failure path rather than the happy one, the operator rather
than the caller, the second run rather than the first, the surface nobody has opened yet.

The asymmetry settles it. An extra pass costs one pass. A missed finding costs a builder's
afternoon, ships a defect, or arrives after the work has started and has to chase it. Buy the
cheap thing.

A unit that feels finished is the cue to run two more passes, not the cue to stop.

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

A unit is atomic when two consecutive passes return nothing new and every remaining piece fails
the separability test. That is the exit condition. Record it on the issue, with the argument,
so the next reader inherits the conclusion rather than the question.

## When work is already running

A correction found after a build session has started must reach that session, not only the
tracker. The session read the issue once, at spawn, and reads none of the conversation that
follows. Send it the finding directly, say plainly whether it changes what they are building,
and say what is deliberately not theirs.

Get both empty passes in before spawning. That is the last moment a correction arrives ahead of
the person acting on it, and it is exactly where the optimistic stop rule does its damage:
declaring the plan finished is what authorises the spawn, so a pass skipped there is a finding
that now has to chase a builder mid-change.

## Scope discipline

Two failures recur, and they pull in opposite directions.

1. **Fixing the instance rather than the class.** One call site corrected while three more
   carry the same mistake.
2. **Fixing past the class.** A correction generalised into places it does not belong, which is
   how a change grows until nothing can review it.

When a pass turns up a defect that predates the work, file it separately rather than absorbing
it. Name it on both issues so neither reader loses it. A unit that fixes everything it touched
on the way past is no longer atomic.
