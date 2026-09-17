# Optional policy modules

Two policies that only some repositories need. Neither belongs in every repo,
so neither ships inside `CLAUDE.md`. When a repo needs one, move it into the
**Repo-specific policy** section of `CLAUDE.md`, adapt the names to the repo,
and delete it from here. When the repo needs neither, delete this file.

Both come out of the `trading-strategies` repository, where each was written
after the failure it prevents had already happened once.

## Module 1: research pins

Take this module when the repo's prose quotes measured numbers. A backtest
result, a benchmark, a reproduction of a published figure, a survey count: any
number a reader could check, and that moves when the code moves.

### The test is the single authority for a quoted number

Every quoted figure traces to an assertion in the test suite. Prose states
these numbers and never derives them. A document that recomputes a number is a
second implementation of the calculation, and the two drift without either one
looking wrong.

When a regression test is re-pinned, the prose that quotes it moves in the same
change. Grep the rounded and spelled-out forms too, since a narrative quotes
`268,000` and `$268K` where a table quotes the exact value.

### Pin a null result rather than leaving it ephemeral

When an experiment kills an idea, record it. A cheap check that is not written
down gets re-derived from scratch every session, and the same dead end costs
the same afternoon twice.

Three surfaces, and a null result needs all three.

1. The code that produced it, deterministic and seeded, applying the same data
   hygiene the rest of the repo applies.
2. A regression test pinning the decisive output, meaning the wrong-signed
   statistic or the percentile that failed, not every intermediate.
3. A human-readable entry in the negative-results log, saying what was tried
   and what killed it.

### Keep the epistemic label loud on every surface

An exploratory result and a registered result are different objects, and a
reader who confuses them draws a conclusion the evidence does not support.

- **Exploratory** means the sample was spent looking. The result kills an idea
  or justifies a closer look. It is never a verdict, however good the number.
- **Registered** means the hypothesis was committed before the number was
  seen. Only a registered result can confirm anything.

A result that passes an exploratory check earns a registration, not a headline.
Registered work lives in its own results doc with its own pins, separate from
the exploration log.

### What promotes a result is out-of-sample evidence, not an explanation

A mechanism is a prior, not a requirement. A story about why an effect should
exist raises the odds that a result will persist, so a coherent one earns trust
on less out-of-sample evidence. It is not a truth condition, and an unexplained
effect is still an effect.

The arbiter is survival on a true holdout, after costs. A result that clears
that bar promotes whether or not anyone can explain it. A persuasive
explanation that has not cleared it does not promote. Dropping the mechanism
requirement makes the out-of-sample discipline more load-bearing, not less.

### Searching many hypotheses needs its own honesty rail

Automating a search multiplies the chance that something looks significant by
accident, so significance is judged across the whole batch under a declared
false-discovery-rate control rather than one candidate at a time.

The hypothesis space is finite, enumerable, and written down before the search
runs. A search that can reach an unbounded set of hypotheses has no honest
denominator.

Hold data back. Commit a subset the search never loads, since a loop cannot
commit to a hypothesis before seeing the number and a held-back subset is the
substitute for pre-registration that automation allows.

## Module 2: cross-surface sweeps

Take this module when the repo has more than one prose surface describing the
same code, or any generated artifact checked into the tree.

### Name the surfaces and what drifts between them

List every surface and what each one is for. Then list what can go stale
without anything failing.

- **Line anchors** in links of the form `file.py#L12`. Adding or moving lines
  in a referenced file breaks these silently.
- **Symbol names** cited in prose. A rename leaves the old name in the doc.
- **Textual line references** written as `file.py:120` in prose rather than as
  a link. An anchor sweep cannot see these at all, so prefer a behavior-preserving
  edit that is line-count-neutral, and sweep the citing docs when lines must move.
- **Pinned numbers**, covered by module 1.
- **Figure embeds**, where the image, its alt text, and its caption all restate
  the same result and must move together.
- **Generated artifacts**, which are a regeneration obligation rather than a
  sweep target. A notebook built from a doc is stale the moment the doc changes.

### Sweep before reporting a change done

```bash
# Every line anchor, confirming each still points at the right symbol
rg '\.py#L\d+' README.md docs/*.md

# Textual line references, which the anchor sweep above cannot see
rg -n --pcre2 '[a-z_]+\.py:\d' docs/*.md

# Every figure embed resolves to a file that exists
rg -o '\]\((?:\.\./)?docs/figures/[0-9A-Za-z_]+\.png\)' docs/*.md \
  | sed -E 's|\]\((\.\./)?||;s|\)||' \
  | while read -r p; do [ -f "$p" ] || echo "MISSING $p"; done
```

Keep any symbol list in these sweeps current with the code's public surface.
Renaming a symbol means updating the sweep in the same change, or every later
sweep quietly checks for a name nothing uses.

### Regenerate in the same change

A mechanical consequence of an edit is the second half of that edit, not a
separate decision. When a change leaves a generated artifact stale, regenerate
it and commit it alongside, without asking. This holds even when the
surrounding conversation is asking for narrower scope, because the narrowing
applies to new work and not to the consequences of work already done.

A no-op diff from a regeneration is a successful regeneration, not a skipped
one. A large or unrelated diff means a stale generator or a mismatched
environment, so investigate rather than committing the churn.

### Report what was swept

End a code-change response with a short **Consistency sweep** note listing what
was checked, what was updated, and what is still stale. For a pure-internal
refactor that moves no line numbers and changes no observable behavior, say
"no prose-facing surfaces affected" so it is clear the check was considered
rather than forgotten.
