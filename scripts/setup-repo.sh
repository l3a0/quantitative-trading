#!/usr/bin/env bash
#
# Apply this template's GitHub-side policy to a repository.
#
# Four things live on GitHub rather than in tracked files, so a fresh clone of
# the template carries none of them.
#
# 1. The branch ruleset that makes `main` require a pull request, read from
#    .github/rulesets/default.json.
# 2. The label set that the triage rule in CLAUDE.md expects to exist, read
#    from .github/labels.json.
# 3. CodeQL's default setup, which the ruleset's code scanning rule waits on.
# 4. GitHub Pages, with GitHub Actions as its source, which the build board's
#    workflow deploys to.
#
# Reading the first two from the repo's own files keeps those files the source
# of truth.
#
# It is idempotent. Running it twice updates in place rather than duplicating.
#
# Usage:
#   scripts/setup-repo.sh l3a0/new-repo
#   DRY_RUN=1 scripts/setup-repo.sh l3a0/new-repo
#
# The ruleset requires two status checks by name, `test` and `docs`, which are
# the two jobs in .github/workflows/ci.yml. Renaming a job means editing the
# ruleset JSON and re-running this script, or the required check goes missing
# and a pull request reports a short rollup rather than a failure.
#
# `strict_required_status_checks_policy` is off, so a branch merges without
# being brought up to date with `main` first. What that setting buys is one
# thing: a run is computed against one merge ref, a later merge to the base
# replaces it, and a rollup can read green after the branch underneath it has
# gone stale. What it costs is charged to every branch rather than to the stale
# ones, because any merge to `main` sends all the open branches back for another
# round of checks.
#
# The staleness is real and is handled by reading rather than by blocking.
# `CLAUDE.md` already requires a session to re-read a rollup whenever the base
# has moved, and that rule does the work this setting was doing, on the branches
# where it matters rather than on all of them.

set -euo pipefail

repo="${1:-}"
if [[ -z "$repo" ]]; then
  echo "usage: $(basename "$0") <owner/repo>" >&2
  exit 2
fi

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ruleset_file="$root/.github/rulesets/default.json"
labels_file="$root/.github/labels.json"

for file in "$ruleset_file" "$labels_file"; do
  if [[ ! -f "$file" ]]; then
    echo "missing $file" >&2
    exit 1
  fi
done

dry_run="${DRY_RUN:-}"

run() {
  if [[ -n "$dry_run" ]]; then
    echo "[dry-run] $*"
    return 0
  fi
  "$@"
}

echo "== $repo =="

# --- Ruleset -----------------------------------------------------------------
# Match on the name rather than an id, since an id belongs to one repository
# and this file is copied between them. --paginate because the endpoint returns
# 30 rulesets a page without saying so, and a miss here creates a duplicate.
ruleset_name="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["name"])' "$ruleset_file")"
existing_id="$(gh api --paginate "repos/$repo/rulesets" --jq \
  ".[] | select(.name == \"$ruleset_name\") | .id" 2>/dev/null | head -1 || true)"

if [[ -n "$existing_id" ]]; then
  echo "updating ruleset '$ruleset_name' (id $existing_id)"
  run gh api --method PUT "repos/$repo/rulesets/$existing_id" --input "$ruleset_file" >/dev/null
else
  echo "creating ruleset '$ruleset_name'"
  run gh api --method POST "repos/$repo/rulesets" --input "$ruleset_file" >/dev/null
fi

# --- Labels ------------------------------------------------------------------
# `gh label create --force` updates an existing label rather than failing, so
# the same call covers both cases. Labels the repo already has and this file
# does not name are left alone, because deleting one detaches it from every
# issue that carries it.
while IFS=$'\t' read -r name color description; do
  echo "label: $name"
  run gh label create "$name" \
    --repo "$repo" \
    --color "$color" \
    --description "$description" \
    --force >/dev/null
done < <(python3 - "$labels_file" <<'PY'
import json
import sys

for label in json.load(open(sys.argv[1])):
    print(f"{label['name']}\t{label['color']}\t{label['description']}")
PY
)

# --- Code scanning -----------------------------------------------------------
# The ruleset carries a code_scanning rule naming CodeQL, and that rule needs
# CodeQL to actually run. Without default setup enabled, the rule waits on a
# tool that never reports. `actions` is in the language list because the
# workflows are part of the attack surface, not only the Python.
# `javascript-typescript` is there because the build board's page,
# .claude/skills/update-build-board/board.html, is JavaScript, and a list
# without it would stop CodeQL scanning that page. GitHub reports the live
# setup with `javascript` and `typescript` as well, which are its aliases for
# the same language.
#
# The body goes in as JSON rather than as --raw-field pairs, because the
# language list is an array and the flag form encodes it as strings.
codeql_body='{"state":"configured","query_suite":"default","threat_model":"remote","languages":["actions","javascript-typescript","python"]}'
echo "code scanning: CodeQL default setup"
if [[ -n "$dry_run" ]]; then
  echo "[dry-run] gh api --method PATCH repos/$repo/code-scanning/default-setup --input - <<< $codeql_body"
elif ! printf '%s' "$codeql_body" \
  | gh api --method PATCH "repos/$repo/code-scanning/default-setup" --input - >/dev/null 2>&1; then
  echo "  could not configure CodeQL. It needs code pushed and a language" >&2
  echo "  GitHub recognises, so re-run this script after the first push." >&2
fi

# --- Pages -------------------------------------------------------------------
# .github/workflows/board.yml publishes the build board on GitHub Pages through
# the github-pages environment, and its deploy job has nowhere to go until
# Pages is on with GitHub Actions as its source rather than a branch. The site
# is read first, so a repository already set that way is left alone and one
# publishing from a branch is switched.
#
# The exit status decides whether a site exists, not the output. A repository
# with no site answers 404, and `gh` prints that error's JSON body to stdout,
# where `--jq` never runs, so the output alone would read as a source type.
if ! pages_type="$(gh api "repos/$repo/pages" --jq .build_type 2>/dev/null)"; then
  pages_type=""
fi
if [[ -z "$pages_type" ]]; then
  echo "pages: enabling, source GitHub Actions"
  run gh api --method POST "repos/$repo/pages" -f build_type=workflow >/dev/null
elif [[ "$pages_type" != "workflow" ]]; then
  echo "pages: switching source from $pages_type to GitHub Actions"
  run gh api --method PUT "repos/$repo/pages" -f build_type=workflow >/dev/null
else
  echo "pages: already on, source GitHub Actions"
fi

# --- Reserved human steps ----------------------------------------------------
cat <<'NOTES'

Done. Three steps stay with a human, because nothing here can guess them.

1. Milestones. Create one per grouping the repo files work under. A filed issue
   needs a milestone or it appears in no grouped view.
2. The premise. Fill the slot at the top of CLAUDE.md and the premise section
   in docs/design.md. Every ranking decision appeals to it, so it comes first.
3. The package name. Rename src/project/ and update the `packages` entry in
   pyproject.toml to match.
NOTES
