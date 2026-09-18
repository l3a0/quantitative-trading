# CLAUDE.md — quantitative-trading

This repo tracks experiments and replications from Ernest Chan's quantitative
trading books. A replication reproduces one published number against data
committed alongside the result, and records a verdict on the gap. Code lives in
`src/chan`, with tests under `tests/`, and [README.md](README.md)'s `## Status`
names what runs today.

**The premise is the vintage.** Vendors restate price history, so an adjusted
close is a function of the download date rather than a property of a trading
day. A number computed from a series nobody kept is a number nobody can check,
including its author. Everything else here is regenerable. That asymmetry is
what every ranking decision below appeals to, and
[docs/design.md](docs/design.md) carries the full reasoning.

**The tracker is authoritative for scope.** An unbuilt deliverable's issue is the source of truth for what it is and what it must do. The design doc at [docs/design.md](docs/design.md) carries the reasoning, the premise, and the considered-and-rejected register, and it links to the issue rather than competing with it. The design doc's `## How work is cut and ordered` carries the rules behind the order, meaning how a deliverable is cut, what an experiment pins, and the reading debt that constrains what can go next. The order itself is on the tracker, in each issue's own statement of what it waits on. Read an unbuilt deliverable's issue before proposing a change to it. Read the design doc for everything else, which includes every built deliverable and the reasoning behind all of them.

The price of this is named rather than hidden: the same substance now exists in an issue and in the doc that reasons about it, so the two can drift. The issue wins. When they disagree, the doc is what gets corrected.

## Rank work by what makes the product usable

Whatever the premise names as the thing that must not fail ranks first, and the tracker carries the order, in each issue's own statement of what it waits on. This directive decides what to take next from the work those two allow, and what decides it is not severity. Before proposing an order, name what is missing from the shortest path to a product someone can use, and put that first.

Then ship it, use it, and let what breaks set the order after that. Evidence from real use outranks any ranking made in advance, including this one.

For everything else in the product's own code, ask how many times the path has run, and give the count. Zero means defer the work, and write the deferral on its issue so the next reader finds it rather than only the next message.

Three exceptions come from the same reasoning.

1. A path that can lose or corrupt data the project cannot recapture is never deferred. That data is gone forever, while everything computed downstream is regenerable.
2. An alarm reads zero while it is healthy, so the count says nothing about it. Dead-man checks, watchdogs, canaries, and backups sit outside this rule. Count the cycles they watched, not the times they fired.
3. A guard whose price is paid by building it late is not cheaper deferred. A read path that must exclude flagged data is inert until something flags any, and adding the exclusion afterwards leaves a second read path that skips it.

Three measurements in the sibling `marketlake` repository produced this rule, and they are cited here as the evidence behind it rather than as facts about this repo.

1. Its daemon slice stood at 43 issues closed and 32 open while its read-layer slice stood at 0 closed.
2. Its lake held 9,839,816 rows captured on a single day and no supported way to read any of them.
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

The price is a pass over the files before work starts, paid on issues whose files have moved. The same evidence that sets the trigger also bounds it. In the repo the rule came from, two audits found something, both on issues naming code that was still moving that day, and seventy closed issues before them are not cited.

## Check the sibling repo before building infrastructure

The files in the table below were written in the sibling
[trading-strategies](https://github.com/l3a0/trading-strategies) repo first, and
the paragraph under that table says which of them are still here. At `b27222b`
that repo held 97 Python files, 42,713 lines of them, built against the same
problem, so a module this repo needs may already exist there. Writing a second
one costs what the research pins below say a second implementation always
costs.

### Sharing beats porting when both repos need the same thing

A port makes a second copy, and a second copy of one calculation drifts
without either one looking wrong. So when a candidate would be used by both
repositories rather than adapted for this one,
[ithildincore](https://github.com/l3a0/ithildin-core) is where it goes. That package
is the shared home, and its own `CLAUDE.md` carries the bar: two repositories,
not two call sites.

Two modules have gone that way already, and each shows one of the two routes
in. `timeseries` was already duplicated here and next door, so sharing it
removed a copy. `stats` had eleven consumers next door at `b27222b` and none
here, and went in because this repo's next significance claim needs it and
relocating exercised code is not the same as building something new.

Sharing costs more than porting, which is why it is not the default for
everything. A shared module can only change through a release, and a change to
one of its function bodies re-pins every consumer. A port can change here
whenever this repo needs it to. So the question is not which is cleaner, it is
whether the other repository would use the same code or a cousin of it.

### Reads that come before a port

Two of them, and both come before the work rather than after it. Search the sibling for what
the issue needs, and read the considered-and-rejected register in
[docs/design.md](docs/design.md), which is what stops a cut thing being
re-proposed. Write what the search found on the issue, alongside the plan audit
above, since both answer the same question at the same moment: what does the
builder need to know that the issue does not say yet. A search that found
nothing still writes its sentence, unlike an audit that found nothing, because
an empty audit leaves the plan standing and the issue already says the plan,
while an empty search answers a question nothing else records.

### A port is cheap in code and expensive in prose and tests

Measured across the six files that already came over, this repo at `f35ffcc`
against the sibling at `b27222b`, counting tokens with comments, blank lines
and indentation markers dropped:

| File | Ported from | Tokens there | Tokens here |
| --- | --- | --- | --- |
| `src/chan/paths.py` | `common/paths.py` | 50 | 50 |
| `src/chan/timeseries.py` | `common/timeseries.py` | 430 | 430 |
| `src/chan/pair_cointegration.py` | `search/pair_cointegration.py` | 2,111 | 2,147 |
| `src/chan/regime_figure.py` | `search/make_regime_figure.py` | 879 | 900 |
| `tests/test_timeseries.py` | `tests/test_timeseries.py` | 391 | 391 |
| `tests/test_pair_cointegration.py` | `tests/test_pair_cointegration.py` | 1,494 | 2,206 |

Two of those files are no longer here. `src/chan/timeseries.py` and
`tests/test_timeseries.py` went to `ithildincore` once the duplication was
measured, which is what the first subsection above is about. The table is
kept at `f35ffcc`, when all six were, because what it measures is what a port
costs and that does not change.

The code barely moved. Only `regime_figure.py` gained an argument, so a test
could draw the figure without overwriting the committed image. The 36 tokens
in `pair_cointegration.py` are two import renames, two new locals, a reworded
line of output, and one ternary expanded into a branch naming a third price
basis. Comparing the two files with docstrings stripped, no function signature
changed at all.

Three rows read as no change and two of those readings are wrong, which is the
warning this table carries. `paths.py` went from `parents[1]` to `parents[2]`
for the deeper `src/chan/` layout, and `tests/test_timeseries.py` repointed
its import from `common` to `chan`. A token count sees neither. Only
`timeseries.py` survives the check: stripping the docstrings from both sides
leaves two files that parse to the same tree, and what still differs on the
page is comments and where one signature wraps. So diff a port against its
source rather than trusting a count, and strip the docstrings before reading
the diff, because they are most of it.

The remaining test file is where the work went. It grew by 712 tokens, close
to half again, because a pinned number here names its vintage and its
specification and the sibling's suite was not written to that rule. Budget a
port as a rewrite of its prose and an extension of its tests. The copying is
the part that takes minutes.

The price of measuring another repository is that this suite cannot assert any
of these numbers, so nothing here notices when the sibling moves. That is why
the commit is named. Re-measure against a newer one rather than editing a cell.

### Say which of three shapes the fit is

A sibling module maps onto a deliverable here in one of three ways, and
calling the wrong one ships a port that does not answer the issue. One
measured example of each, all read at `b27222b`.

1. **Direct, which means it belongs in `ithildincore` rather than here.** The
   worked example is `common/stats.py`, 88 lines of Newey-West standard errors
   that needed no adaptation at all, so copying it would have made a second
   copy of code neither repo had a reason to diverge on. It went to the shared
   package. Its module docstring did not: that was entirely about campaign
   cells and an engine version that do not exist here, which is the cost split
   the table above measures. A direct fit is the signal to share, not to
   port.
2. **Partial.** `common/position_sizing.py` carries `kelly_fraction`, and
   [issue 14](https://github.com/l3a0/quantitative-trading/issues/14) has
   already ruled on it under a heading that says not to reuse it. The discrete
   form over a bag of per-trade outcomes is a different object from the
   continuous form on one return series' moments. Same idea, different
   formula. Nothing in that function transfers, including the grid search and
   the absorption boundary at `1 / |min r|`, which exists only because a
   discrete bag has no closed-form optimum. The idea transfers and the issue
   is where that was settled, so a search reaching the module without the
   ruling re-opens a decided question.
3. **None.** `pipeline/validate_dailies.py` is 580 lines whose name suggests
   [issue 2](https://github.com/l3a0/quantitative-trading/issues/2), which
   verifies a vintage before a run reads it. It validates option-chain greeks
   against an entry band and shares nothing with a vintage check.
   `pipeline/download_prices.py` is 41 lines that write a CSV and stop, while
   [issue 1](https://github.com/l3a0/quantitative-trading/issues/1) wants a
   manifest, a checksum, a path naming that keeps two vintages of one symbol
   apart, and a refusal to overwrite that the issue's own notes call the part
   worth getting right. The vintage machinery is this repo's own idea and has
   to be built here.

### Four things never come across

1. **The prose.** The sibling's `CLAUDE.md` is a blog-writing prompt, and its
   docstrings shout in capitals and open on its own vocabulary. Every ported
   docstring here was rewritten, which is what every changed line in
   `timeseries.py` is.
2. **The vocabulary.** A ported module carries terms that mean something next
   door and nothing here. The design doc's pinned vocabulary wins, and a term
   with no entry there gets replaced by what happens.
3. **The dependencies.** `pyproject.toml` carries the `dependencies` list this
   repo runs on. A port needing another entry is a decision that belongs in the
   pull request body rather than in a line nobody argued about.
4. **The evidence.** The ranking directive counts how many times a path has
   run, and it means here. A ported path has run zero times in this repo
   whatever it did next door. Where the sibling's count is the argument, cite
   it as the sibling's, the way the `marketlake` numbers above are cited. The
   tests are what carry the confidence over, so they land in the same change
   or the port arrives with no pins at all.

A copied file that is not code is its own case. A CSV is a vintage, so it
arrives with its row in [data/README.md](data/README.md) naming vendor,
symbol, span, download date and price basis, and its line in
`data/checksums.sha256`. A figure arrives with the code that redraws it and a
test that pins what it draws, which is what
[PR #25](https://github.com/l3a0/quantitative-trading/pull/25) did for
`docs/figures/reproduction_regime_map.png`.

### Reuse is the default, and a declined port gets a register row

Port by default. Where a port is declined, pin it in the design doc's
considered-and-rejected register, which exists so a decision stays decided.
A reason written only next to the thing it affects is a reason the next
session searching the register will not find, and it re-proposes the port.

### Every port names its source and its changes

A ported file that does not name where it came from cannot be diffed against
its original, which throws away the one cheap check the table above shows is
worth running. So a port names the sibling file, the commit it was taken from,
and what changed on the way over, in the module docstring.
[PR #25](https://github.com/l3a0/quantitative-trading/pull/25) is the pattern
for prose: `README.md` names the sibling and lists all three changes.

None of the four still here does this yet, which is what
[issue 29](https://github.com/l3a0/quantitative-trading/issues/29) back-fills.
The two that went to `ithildincore` carry it there, in that package's `README.md`
and in the release its tag points at.

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

- **The test suite is the single authority for any number the prose quotes.** Prose states these numbers and never derives them. `tests/test_pair_cointegration.py` derives what the replications quote, 1.6379 and 1.3905 among them, and `tests/test_regime_figure.py` derives what the figure draws. Some figures cannot be derived here at all, and the rule for those is to name them as unpinned rather than let them read as asserted. 1.6766 is one, a number Chan printed that no modern download reaches, so the suite cites it as a book target and asserts only the distance from it. `README.md`'s `## The write-up` lists the rest.
- **The design doc is the single authority for reasoning.** Code comments point at it rather than restating it.
- **The issue is the single authority for unbuilt scope**, per the tracker directive above.

### The sweep policy applies here

It was deferred on a count of zero and
[issue 6](https://github.com/l3a0/quantitative-trading/issues/6) wrote down
what would reopen it. All three triggers have fired, so the owner kept it on
2026-09-18 and this is where it lives.

This repo has ten prose surfaces: nine Markdown files and
`docs/gld-gdx-cointegration-lessons.html`. That HTML file is the sharp case,
because it is a second rendering of `blog/gld-gdx-cointegration-lessons.md`
rather than a document of its own, and nothing generates it from the Markdown.

**The one figure exists in three copies, and two of them are not files.**

1. `docs/figures/reproduction_regime_map.png`, drawn by
   [src/chan/regime_figure.py](src/chan/regime_figure.py).
2. A base64 copy inlined in the HTML, so the page is self-contained.
3. An embed in the blog Markdown pointing at copy 1.

Redrawing the figure updates one of the three. That is what
`test_the_inlined_figure_matches_the_committed_png` in
[tests/test_markdown_hygiene.py](tests/test_markdown_hygiene.py) is for. It
compares the inlined bytes against the file and fails when a redraw touches
only one, because a policy nothing executes is a policy that holds until the
first time it matters.

Two of the template's sweeps have nothing to check here yet, and saying so is
the point rather than an omission. No link and no sentence in this repo names a
line of a source file, measured at `aec40f3`. Keep it that way: a prose
reference names a symbol, which survives an edit, rather than a line, which
does not.

`test_no_prose_surface_names_a_line_number` is what keeps it that way, and
writing it turned up two things worth knowing. It caught the first draft of
this paragraph, which spelled the forbidden form out as an example and so
became an instance of it. Describing the shape rather than writing one is the
fix, and a rule that cannot state itself is worth noticing. It also needed
`blank_fences` rather than `blank_code`, because a reference in prose is
normally written in backticks and `blank_code` blanks those, which is right for
the tilde and table sweeps and would have made this one pass on anything a
person would actually write.

```bash
# Every figure embed resolves to a file that exists
rg -o '\]\((?:\.\./)?docs/figures/[0-9A-Za-z_]+\.png\)' *.md docs/*.md blog/*.md \
  | sed -E 's|\]\((\.\./)?||;s|\)||' \
  | while read -r f; do [ -f "$f" ] || echo "MISSING $f"; done

# Line references, which should stay empty
rg -n --pcre2 '[a-z_]+\.py[:#]L?\d' *.md docs/*.md blog/*.md
```

**Regenerating is the second half of an edit, not a separate decision.** When a
change leaves the figure stale, redraw it and commit it in the same change,
without asking. A no-op diff from a redraw is a successful redraw rather than a
skipped one. A large diff means a stale generator or a mismatched environment,
so investigate instead of committing the churn. `docs/figures` is also why
`matplotlib` is a dev dependency rather than a runtime one.

Before reporting a code change done, sweep the prose surfaces for what the change could have invalidated, and end the response with a short **Consistency sweep** note listing what was checked, what was updated, and what is still stale. For a pure-internal refactor that moves no line numbers and changes no observable behavior, say "no prose-facing surfaces affected" so it is clear the check was considered rather than forgotten.

A mechanical consequence of an edit is part of that edit, not a separate decision. When a change leaves a generated artifact stale, regenerate it in the same change without asking.

## Secrets and machine paths

This repo is public. Tracked files never carry secrets or machine-specific paths. Machine-local config lives under `~/.config/quantitative-trading/`, and the design doc's Configuration section states the full rules. Sweep for leaks before any publish.

No vendor used so far needs a credential, so the repo holds no secrets today. That changes the first time a paid data source lands, and the design doc's Configuration table is where it gets named.

Committed data is a separate question from secrets. A vintage is committed on purpose, because the premise says a result nobody can re-read is a result nobody can check. What does not get committed is anything that identifies a machine or a person.

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

Three behaviours make the rule sharper than "look for a green tick". The first two were measured on pull requests in the sibling `marketlake` repo, and the third on the template this repo was seeded from.

1. **A conflicting pull request gets no run at all.** A `pull_request` workflow builds the merge ref, and a branch that conflicts has none, so no run is created. PR #414 there showed three green CodeQL entries and no `test` run whatsoever. An absent check reads as a short rollup rather than as a failure, so count what ran instead of scanning for red.
2. **Green goes stale.** A run is computed against one merge ref, and a later merge to the base replaces it. PR #433 there read green after the branch had already conflicted underneath it. Re-read the rollup whenever the base has moved.
3. **Red goes stale the same way, and costs more.** A failure inherited from the base survives in the rollup after the base has been fixed. A pull request on the template carried a red `test` check from a run computed 25 seconds before the pull request that fixed its base merged. Rebasing made it green, and a monitor reading the older snapshot reported the failure again afterwards. A red check is a claim about one merge ref at one moment, so re-read it before acting, and check whether the pull request has already merged before fixing anything.

Fix the cause rather than the symptom. A lint rule that fails on one file usually fails on its siblings, so sweep for the class. Re-running a job changes nothing the second time unless the failure was the runner rather than the code. Where a failure comes from another branch's merge rather than from this change, say so on the pull request instead of absorbing an unrelated fix into it.

**A filed issue carries its milestone and its labels.** Filing is not finished when the issue exists. An issue with no milestone appears in no grouped view and no view scoped by kind, so only a sweep for nulls finds it, and nothing brings it back on its own. So a filed issue is finished when it says three things.

1. A milestone says which grouping owns it.
2. A label says what kind of work it is.
3. A dependency says what it waits on, where it waits on anything.

No automation supplies the first two. The same applies to an issue a spawned session is told it may file. The instruction to file carries the instruction to triage, or the work lands where nothing will look for it.

**Close an issue only when nothing is left in it.** Before a PR closes an issue, move whatever that PR does not do into its own issue. A piece described only inside a body goes when the body closes, and nothing surfaces it again.

While a piece is outstanding, a PR writes `Part of #NN` and the closing keyword waits for the PR that leaves nothing. GitHub reads the keyword only when the number follows it immediately, so `Closes the second half of #101` closes nothing at all. The keyword also has to be plain text, and a code span around it defeats it the same way. That is how PR #34 merged without closing issue 6. Writing the working form here would make this sentence an instance of it, so the shape is described rather than shown. Rendered, a code span and plain text differ only in font, so reading the body back does not distinguish them. `gh pr view <n> --json closingIssuesReferences` does, and an empty result on a pull request that means to close something is the signal to fix the body before merging.

An issue whose pieces have all been split has no finishing PR left, so close it by hand and name where each piece went. Do the same when two PRs are open against one issue, because merge order decides which lands last and neither body can know it. A split leaves code comments pointing at the parent for work that moved, so repoint those in the PR that splits. A comment naming a closed issue in the past tense records what happened rather than pointing anywhere, and it stays.

PR titles use a Conventional Commits prefix. The form is `type(scope): summary`. `gh pr list --state merged --json title` reports which prefixes this repo has used, rather than a list here that goes stale on the first unfamiliar one. Add a scope in parens when it sharpens the title, like `docs(CLAUDE.md)`. Drop it when none does, like a plain `docs:` for a whole-doc change.

PR bodies use Markdown section headings, not a wall of prose. Lead with `## Why`, then `## What`. Add situational sections after as the change needs them, like `## Scope`, `## Notes`, or `## Evidence`. The body's prose obeys the writing-style rules above. So clear, short sentences and no em dashes. End every body with the footer line: `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.

## Update the build board when a session finishes

The build board is the page that answers what is in flight and what to take next, and it cannot refresh itself. It reads no disk and polls no API, so every figure on it was measured by hand and baked in. A session that finishes its work and leaves is a session that has just made the board wrong, and nothing else will notice.

So three moments end with a board update, and each is the moment the page's own answer changed.

1. **A decompose loop exits.** The plan is now one somebody has executed against the code, and the board draws that as a state rather than leaving the card reading like every other guess.
2. **A pull request opens or merges.** The card moves out of the build order and into the in-flight section, or out of the tracker entirely.
3. **A review lands on a pull request.** That is the only thing that moves a card from waiting on a reviewer to waiting on the owner, and it is the column the owner reads first.

The `update-build-board` skill under `.claude/skills/` carries the procedure, including which commands measure which figure and how to execute the page before publishing it. Follow it rather than editing the page by eye.

Two things about that update are worth naming rather than discovering.

Measure, never recall. Every figure has a command behind it, and the count carried in your head from earlier in the session is the one that will be wrong. One update shipped 39 open issues against a query that said 40.

Read the live page before editing it. Another session may have republished, a publish over a version nobody read is refused, and a local copy is a guess about what is published.

The price of this rule is real and is accepted on purpose. Every session pays an update, and a session that runs it against stale measurements makes the page worse rather than better, which is why the procedure leads with reading and measuring rather than with editing. The alternative is worse: a page nobody updates is a page that reads as current while describing a repository that has moved, and the first reader to trust it pays more than every skipped update saved.

## Research pins

This repo quotes measured numbers from its first commit, so this section
applies from day one. It came from the sibling `trading-strategies` repo,
where each rule was written after the failure it prevents had happened once.

### Re-pinning a number moves the prose that quotes it

The single-authority rule itself is stated once, under Cross-surface
consistency above. What follows here is what it costs in practice.

A document that recomputes a number is a second implementation of the
calculation, and the two drift without either one looking wrong. So when a
regression test is re-pinned, the prose that quotes it moves in the same
change. Grep the rounded and spelled-out forms too, since a narrative quotes a
figure in words where a table quotes it exactly.

### Every pinned number names its vintage and its specification

A pin with no vintage cannot be re-derived, and a re-pin with no vintage cannot
say what moved. The vintage is part of the assertion, not a note beside it.

The specification belongs there for the same reason. Chan's GLD/GDX example
prints a hedge ratio from a through-origin regression on one window and a test
statistic from a regression with an intercept on another, near enough to each
other to read as one result. A pin that names only the number reproduces that
confusion rather than resolving it.

### Match number precision to the data

Present a number at the precision the data supports, and write the same
quantity the same way everywhere it appears. When reproducing a source's
figure, match the source's precision rather than rounding below a real digit
or inventing one. Round from the true value, not from an already-rounded
printout. Where matching a source's precision would only expose disagreement,
stop at the precision that is real.

### Pin a null result rather than leaving it ephemeral

When an experiment kills an idea, record it. A cheap check that is not written
down gets re-derived from scratch every session, and the same dead end costs
the same afternoon twice.

Three surfaces, and a null result needs all three.

1. The code that produced it, deterministic and seeded, reading a committed
   vintage like anything else.
2. A regression test pinning the decisive output, meaning the wrong-signed
   statistic or the percentile that failed, not every intermediate.
3. A written log entry saying what was tried and what killed it.

### Keep the epistemic label loud on every surface

An exploratory result and a registered result are different objects, and a
reader who confuses them draws a conclusion the evidence does not support.

- **Exploratory** means the sample was spent looking. The result kills an idea
  or justifies a closer look. It is never a verdict, however good the number.
- **Registered** means the hypothesis was committed in writing before the
  number was seen. Only a registered result confirms anything.

A replication is exploratory by construction. Reproducing a published figure
spends the sample on a hypothesis someone else already chose, so it can say
whether the number reproduces and nothing more. A replication that survives
earns a registration, not a headline.

### What promotes a result is out-of-sample evidence, not an explanation

A mechanism is a prior, not a requirement. A story about why an effect should
exist raises the odds that it persists, so a coherent one earns trust on less
out-of-sample evidence. It is not a truth condition, and an unexplained effect
is still an effect.

The arbiter is survival on a true holdout, after costs. A result that clears
that bar promotes whether or not anyone can explain it. A persuasive
explanation that has not cleared it does not promote.

### Searching many hypotheses needs its own honesty rail

Trying many variants multiplies the chance that something looks significant by
accident. Where that happens, significance is judged across the whole batch
under a declared false-discovery-rate control rather than one candidate at a
time, the hypothesis space is written down before the search runs, and some
data is held back that the search never loads.

None of that applies to a replication, which tests one number chosen by
someone else. It applies the moment this repo starts varying parameters to see
what works.
