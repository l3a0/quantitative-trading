# CLAUDE.md — PROJECT_NAME

<!-- TEMPLATE: replace this paragraph with the repo's premise. Say what the
     project is, what it is for, and where the reasoning lives. Two or three
     sentences. The premise is what every later ranking decision appeals to,
     so write it before writing anything else. -->

PROJECT_NAME is TODO. Status: TODO. Code lives in `src/`, with tests under `tests/`.

**The tracker is authoritative for scope.** An unbuilt deliverable's issue is the source of truth for what it is and what it must do. The design doc at [docs/design.md](docs/design.md) carries the reasoning, the premise, and the considered-and-rejected register, and it links to the issue rather than competing with it. [docs/build-plan.md](docs/build-plan.md) carries the slicing rule, the build order, and each slice's test surface, and its deliverable entries are links. Read an unbuilt deliverable's issue before proposing a change to it. Read the design doc for everything else, which includes every built deliverable and the reasoning behind all of them.

The price of this is named rather than hidden: the same substance now exists in an issue and in the doc that reasons about it, so the two can drift. The issue wins. When they disagree, the doc is what gets corrected.

## Rank work by what makes the product usable

Whatever the premise names as the thing that must not fail ranks first, and [docs/build-plan.md](docs/build-plan.md) carries the slice order and the dependencies between slices. This directive decides what to take next from the work those two allow, and what decides it is not severity. Before proposing an order, name what is missing from the shortest path to a product someone can use, and put that first.

Then ship it, use it, and let what breaks set the order after that. Evidence from real use outranks any ranking made in advance, including this one.

For everything else in the product's own code, ask how many times the path has run, and give the count. Zero means defer the work, and write the deferral on its issue so the next reader finds it rather than only the next message.

Three exceptions come from the same reasoning.

1. A path that can lose or corrupt data the project cannot recapture is never deferred. That data is gone forever, while everything computed downstream is regenerable.
2. An alarm reads zero while it is healthy, so the count says nothing about it. Dead-man checks, watchdogs, canaries, and backups sit outside this rule. Count the cycles they watched, not the times they fired.
3. A guard whose price is paid by building it late is not cheaper deferred. A read path that must exclude quarantined records is inert until something writes a verdict, and adding the exclusion afterwards leaves a second read path that skips it.

Three measurements in the sibling `marketlake` repository produced this rule, and they are cited here as the evidence behind it rather than as facts about this repo.

1. Its daemon slice stood at 43 issues closed and 32 open while its read-layer slice stood at 0 closed.
2. Its lake held 9,839,816 captured rows and no supported way to read any of them.
3. Several rounds of work hardened an overflow column that was non-null on zero of 9,846,266 sealed rows.

Ranking by severity never runs out of work, because any path with no test behind it can be called a failure waiting to happen. That is how three rounds of hardening reached one capture path while the data stayed unreadable.

Cut a large deliverable down to the part that runs against what the project already holds. Its issue stays the source of truth for what the deliverable is, so the cut is proposed there first. The shipping pull request then writes `Part of`, and the issue keeps the remainder, per the closing rule below.

The price of this is named rather than hidden. Shipping the usable path first leaves gaps open on paths nothing has exercised, and one of them will eventually cost something. That is accepted on purpose, inside the three exceptions above. A product nobody can use produces no evidence about which hardening mattered, so the deferred work is also the work with the least evidence behind it.

## Audit an issue's plan before starting work on it

An issue is where a plan lives, and a plan is a hypothesis about work that has not happened yet. What usually makes one wrong is that the files it names moved after it was written. So the trigger is narrow rather than universal. Run `git log` on the files an issue names, bounded by the issue's own date, and audit the plan when they have changed. A plan written against files that have sat still is a plan nothing has invalidated. The session that spawns the work runs the audit before it spawns, since that is the last moment a correction can reach the issue ahead of the reader who acts on it.

Two checks have each already caught something in the sibling repository this rule came from.

1. Check the issue's stated blocker against the current code. One issue said pruning a read down to one record would rest on the writer's incidental row ordering. Parquet skips only the row groups whose statistics prove they cannot match, so ordering decides how many groups are skipped and never which rows come back. A fixture written in deliberately shuffled order returned every row a full read returned, the writer was never involved, and the work stayed in the reader.
2. Read what the code already decided in writing. One module's docstring ended by stating that nothing in it read a config file, which was a deliberate decision. A session meeting that sentence mid-change either deletes it quietly or stops to ask. The issue body had already answered it in advance, so the work arrived knowing what the sentence was protecting and corrected it rather than deleting it.

An audit is a plan too, so it names the commit it was derived against. One audit cited a line number and a call-site count that a merge thirty minutes later moved. Pin line numbers to a named commit and tell the reader to re-sweep for the class rather than trust the list.

A correction goes on the issue, because a spawned session reads the issue and reads none of the conversation that started it. An audit that found nothing reports that to whoever asked for it and writes nothing, since an issue padded with empty notes is harder to read, which is what writing to the issue was meant to protect.

Where the audit finds the code contradicting the issue, the issue still decides what the deliverable is, per the tracker directive above. What changes is that the code's stated reason becomes something the issue answers in advance rather than something the work runs into halfway through.

The price is a pass over the files before work starts, paid on issues whose files have moved.

## Writing style

The owner's global `~/.claude/CLAUDE.md` is the source for these rules. This section repeats them because the repo is public and a reader or an agent may arrive without that file. The price is that the two copies can drift. The global file wins, and this section is what gets corrected.

Clarity comes first. Write plain sentences a reader understands on one read. Prefer short, complete sentences, but never at the cost of clarity. Do not chop an idea into cryptic one-idea fragments. When a short sentence turns hard to parse, write the clear sentence instead, even if it runs a little longer. Explain as you go, like teaching, so the reader follows without backtracking. Avoid em dashes and semicolons. This applies to every prose surface: this file, the design doc, commit messages, pull request bodies, and chat replies.

**Impersonal voice.** Write without the first person. No "I," "my," or "mine." The subject is the process, the mechanism, or the finding, not the author. "Running the script reproduced the result" beats "I ran the script to reproduce it." Keep it active, not passive: "The check reads the config," never "the config is read." Direct advice stays as an imperative. Drop the explicit "you" and "your" where it reads cleaner.

**Explain every concept on first use.** Coined vocabulary, borrowed tools, and non-obvious behaviors get their gloss where they first appear, not in a glossary. If a reader must ask "what is X," the writing failed at X's first appearance.

**Drop the jargon rather than glossing it.** Given the choice between defining an in-group term and deleting it, delete it. The test: when a sentence names a concept where it could say what happens, say what happens. "No test covers it" beats "it is unheld." A gloss works once, at first use, while the term keeps reappearing and costs the reader attention every time. Being native to a repo does not save a term. Cut the whole family at once, since the same idiom usually survives under a second word. One exemption: the design doc's pinned vocabulary, which carries exact definitions and is reused on purpose.

**List a counted set. Do not inline it.** When a sentence names a count of items, like "four seams" or "three tests," the items follow as a list, not a run-on of sentences. Number the list when the prose states the count. Use a bulleted list for an unordered set with no count.

**Lead with why it matters, show the reasoning, and name the price.** Establish why something matters before explaining what it is. State the claim, then walk through why. When a choice carries a cost, name it outright, as in "the price for X is Y." When weighing two options, hand over the metric that decides between them instead of gesturing at "tradeoffs."

**Cut what carries nothing.** Throat-clearing, significance-announcing pivots, self-effort asides, hedging, redundancy, decorative modifiers that survive the subtraction test, unsubstantiated superlatives, reversal scaffolding, reassurance tags, and a closing moral that restates the heading. The global file carries the worked examples for each.

## The design doc carries the reasoning

Two conventions keep [docs/design.md](docs/design.md) usable as the project grows.

- **The considered-and-rejected register.** Cut machinery is pinned in the doc with its rationale, so nothing gets re-proposed after it was decided against. When something new is cut, pin it the same way.
- **Pinned vocabulary.** Terms with exact definitions are listed and reused. Do not coin synonyms for a term the doc already defines.

One lesson is worth keeping in view. Reviews armor what exists. They rarely ask whether it should exist. Ask "why is this needed" before "is this correct."

## Markdown hygiene

Every `.md` file must pass markdownlint, which CI runs on every pull request. The rules that bite most: use real headings, never a bold line as a heading (MD036). No trailing whitespace (MD009). No stacked blank lines (MD012). End the file with exactly one newline (MD047). Table delimiter rows use single-space padding, so `| --- |` and never `|---|` (MD060). Escape an "approximately" tilde in prose as `\~`, since a bare tilde can render as strikethrough on some surfaces. Code fences are exempt.

After any edit, sweep:

```bash
rg -n --pcre2 '(?<![\s~\\`<])~' *.md docs/*.md
rg -n '\|-{1,}\|' *.md docs/*.md
```

When a heading changes, verify the Contents anchors still resolve.

## Cross-surface consistency

A repo drifts when two surfaces describe the same thing and only one gets updated. The fix is to give each surface exactly one job, so nothing is stated twice.

- **The test suite is the single authority for any number the prose quotes.** Every quoted figure traces to an assertion. Prose states these numbers and never derives them.
- **The design doc is the single authority for reasoning.** Code comments point at it rather than restating it.
- **The issue is the single authority for unbuilt scope**, per the tracker directive above.

<!-- TEMPLATE: list this repo's prose surfaces and what can drift between them.
     The sibling `trading-strategies` repo's list is the worked example: line
     anchors of the form `file.py#L12`, symbol names cited in prose, pinned
     numbers, figure embeds, and generated artifacts that must be regenerated
     rather than hand-edited. Delete this section if the repo has one surface. -->

Before reporting a code change done, sweep the prose surfaces for what the change could have invalidated, and end the response with a short **Consistency sweep** note listing what was checked, what was updated, and what is still stale. For a pure-internal refactor that moves no line numbers and changes no observable behavior, say "no prose-facing surfaces affected" so it is clear the check was considered rather than forgotten.

A mechanical consequence of an edit is part of that edit, not a separate decision. When a change leaves a generated artifact stale, regenerate it in the same change without asking.

## Secrets and machine paths

This repo is public. Tracked files never carry secrets or machine-specific paths. Machine-local config lives under `~/.config/PROJECT_NAME/`, and the design doc's Configuration section states the full rules. Sweep for leaks before any publish.

<!-- TEMPLATE: name this repo's secrets and where they live. Credentials,
     tokens, ping URLs, and notification topics are all secrets. A path that
     names a machine or a person is not a secret but still does not belong in
     a tracked file. -->

## Committing

**Commit, push and open the pull request without waiting.** A session that has finished the deliverable it was given commits it, pushes the branch, and opens the pull request on its own. It does not stop to ask first.

An earlier version of this rule asked for explicit approval before every commit. The cost was a session idle on finished work whenever the owner was away from the keyboard, and the approval bought nothing the pull request's own diff does not show better and later.

Three things still hold.

1. `main` requires a pull request. An active repository ruleset enforces it. Owners can bypass that rule, but do not: branch, push, and open a PR, even for a one-line docs change.
2. A commit carries only what the session actually did. Unrelated edits found on the way past are filed as their own issue, per the closing rule below, and never swept into the branch.
3. Work outside the session's own deliverable still waits for the owner. That covers this file and anything under `~/.config/`.

Branch before the first edit, not just before the commit. The moment a task will modify any tracked file, run `git branch --show-current` and branch if it shows `main`. Re-check before every commit, not just the first of a session, because a mid-session squash-merge deletes the branch and leaves the checkout on `main`.

## Pull requests

**Review every pull request before the owner does.** A PR the owner has not seen reviewed is not finished work. This holds whether the PR is yours or someone else's, whether it is one line or a thousand, and whether or not a review was asked for. The owner's time is the scarce thing, so a PR reaches them already checked rather than waiting to be read cold.

**Send the link as soon as the pull request exists, then review it.** Opening the pull request and starting the review are one step, and neither waits on the owner. The link is what lets them watch the review land, so holding it back leaves them blind to work that is already pushed. Post the findings on the pull request, and say plainly what the review found and what it refuted, including when it found nothing.

Review by fanning out independent lenses, then verifying each finding adversarially. Several reviewers in parallel, each with one lens and no sight of the others, produce the findings. Verifiers then try to refute each one, and only what survives is acted on. Point one lens at completeness and one at over-reach, which catch the two failures that recur:

1. Fixing the instance rather than the class, such as a false claim corrected in one file while it still stands in three more.
2. Fixing past the class, such as generalising a change into places it does not belong.

Verify by executing, not by reading. Mutate the code and confirm a test fails. A test that still passes under mutation does not cover what it claims to cover.

**Watch the checks and fix what they find.** A pull request is not handed over until its checks have run and settled. Pushing is not the end of the work, because the branch that passes locally is not the branch CI builds. CI builds the merge of the branch and its base, and the base moves.

So watch the run rather than assume it. `gh pr checks <n> --watch` blocks until every check settles, and `gh pr view <n> --json statusCheckRollup` says what each one concluded. When a check fails, read its log, fix the cause, and push again, in the same session and without waiting to be asked. A red check the owner finds first is work handed over unfinished.

Two measurements make the rule sharper than "look for a green tick".

1. **A conflicting pull request gets no run at all.** A `pull_request` workflow builds the merge ref, and a branch that conflicts has none, so no run is created. An absent check reads as a short rollup rather than as a failure, so count what ran instead of scanning for red.
2. **Green goes stale.** A run is computed against one merge ref, and a later merge to the base replaces it. Re-read the rollup whenever the base has moved.

Fix the cause rather than the symptom. A lint rule that fails on one file usually fails on its siblings, so sweep for the class. Re-running a job changes nothing the second time unless the failure was the runner rather than the code. Where a failure comes from another branch's merge rather than from this change, say so on the pull request instead of absorbing an unrelated fix into it.

**A filed issue carries its milestone and its labels.** Filing is not finished when the issue exists. An issue with no milestone appears in no slice view and no view scoped by kind, so only a sweep for nulls finds it, and nothing brings it back on its own. So a filed issue is finished when it says three things.

1. A milestone says which slice owns it.
2. A label says what kind of work it is.
3. A dependency says what it waits on, where it waits on anything.

No automation supplies the first two. The same applies to an issue a spawned session is told it may file. The instruction to file carries the instruction to triage, or the work lands where nothing will look for it.

**Close an issue only when nothing is left in it.** Before a PR closes an issue, move whatever that PR does not do into its own issue. A piece described only inside a body goes when the body closes, and nothing surfaces it again.

While a piece is outstanding, a PR writes `Part of #NN` and the closing keyword waits for the PR that leaves nothing. GitHub reads the keyword only when the number follows it immediately, so `Closes #101` closes and `Closes the second half of #101` closes nothing at all.

An issue whose pieces have all been split has no finishing PR left, so close it by hand and name where each piece went. Do the same when two PRs are open against one issue, because merge order decides which lands last and neither body can know it. A split leaves code comments pointing at the parent for work that moved, so repoint those in the PR that splits. A comment naming a closed issue in the past tense records what happened rather than pointing anywhere, and it stays.

PR titles use a Conventional Commits prefix. The form is `type(scope): summary`. Types in use: `docs`, `feat`, `fix`, `refactor`, `chore`, `ci`, `perf`. Add a scope in parens when it sharpens the title, like `docs(CLAUDE.md)`. Drop it when none does, like a plain `docs:` for a whole-doc change.

PR bodies use Markdown section headings, not a wall of prose. Lead with `## Why`, then `## What`. Add situational sections after as the change needs them, like `## Scope`, `## Notes`, or `## Evidence`. The body's prose obeys the writing-style rules above. So clear, short sentences and no em dashes. End every body with the footer line: `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.

## Repo-specific policy

<!-- TEMPLATE: policy that only this repo needs goes here. Two modules ship
     with the template in docs/optional-policies.md, ready to move into this
     section when the repo needs them:

       1. Research pins, for a repo whose prose quotes measured numbers.
       2. Cross-surface sweeps, for a repo with generated artifacts.

     Delete this heading if the repo needs neither. -->
