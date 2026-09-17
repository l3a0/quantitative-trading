# repo-template

A starting point for a new repository: the agent instructions, the CI, and the
GitHub-side policy that the [marketlake](https://github.com/l3a0/marketlake)
and [trading-strategies](https://github.com/l3a0/trading-strategies)
repositories converged on, in one place a new repo can start from.

Those two repos grew the same rules twice, in different words, and drifted. One
example: they gave opposite committing instructions, because a directive
written to replace the other never reached the second repo. This template is
the merged version, so the next repo starts from the settled rule rather than
from whichever copy it was cloned off.

## What it carries

- **[CLAUDE.md](CLAUDE.md)** is the agent instruction file. Scope authority,
  how to rank work, plan audits, writing style, markdown hygiene, secrets,
  committing, and pull request review. It has template slots for the premise
  and for repo-specific policy, marked as HTML comments.
- **[.github/workflows/ci.yml](.github/workflows/ci.yml)** runs two jobs. `test`
  runs ruff, a format check, and pytest under uv. `docs` runs markdownlint.
  The ruleset requires both by name.
- **[.github/rulesets/default.json](.github/rulesets/default.json)** makes
  `main` require a pull request, a squash merge, linear history, CodeQL, and
  both status checks. It is the ruleset both sibling repos run, with the
  required checks retargeted and the stale-green gap closed.
- **[.github/labels.json](.github/labels.json)** is the label set the triage
  rule in CLAUDE.md expects to exist.
- **[.github/dependabot.yml](.github/dependabot.yml)** groups minor and patch
  bumps, keeps majors separate, and keeps ruff on its own so a new lint rule
  never turns an unrelated pull request red.
- **[scripts/setup-repo.sh](scripts/setup-repo.sh)** applies the ruleset, the
  labels, and CodeQL default setup to a repository. It is idempotent and takes
  `DRY_RUN=1`.
- **[docs/design.md](docs/design.md)** and
  **[docs/build-plan.md](docs/build-plan.md)** are skeletons for the two docs
  CLAUDE.md refers to by name.
- **[docs/optional-policies.md](docs/optional-policies.md)** holds two policy
  modules that only some repos need, ready to move into CLAUDE.md.
- **[tests/test_markdown_hygiene.py](tests/test_markdown_hygiene.py)** runs the
  two prose sweeps CLAUDE.md names, so they fail the suite rather than waiting
  for someone to remember the command.

## Starting a repo from it

```bash
gh repo create l3a0/new-repo --public --template l3a0/repo-template --clone
cd new-repo
scripts/setup-repo.sh l3a0/new-repo
```

Then do the four things nothing can guess.

1. Fill the premise slot at the top of `CLAUDE.md` and the premise section in
   `docs/design.md`. Every later ranking decision appeals to it.
2. Rename `src/project/` and update the `packages` entry in `pyproject.toml`.
3. Create one milestone per slice, named as `docs/build-plan.md` names them.
4. Decide whether either module in `docs/optional-policies.md` applies, move
   what does into `CLAUDE.md`, and delete the file.

## Running the checks locally

```bash
uv sync --dev
uv run ruff check
uv run ruff format --check
uv run pytest
```

markdownlint has no Python package, so it runs in CI rather than locally. The
two sweeps it cannot do run in the test suite.

## Why the checks are required rather than advisory

A ruleset that lists no required status check leaves a red job blocking
nothing. marketlake merged 43 pull requests in that state, and a rollup with
no failures in it reads the same as a rollup that passed, so nothing about the
pull request page says the gate is open. This template requires both checks
from the first commit.
