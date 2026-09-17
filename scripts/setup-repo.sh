#!/usr/bin/env bash
#
# Apply this template's GitHub-side policy to a repository.
#
# Two things live on GitHub rather than in tracked files, so a fresh clone of
# the template carries neither: the branch ruleset that makes `main` require a
# pull request, and the label set that the triage rule in CLAUDE.md expects to
# exist. This script applies both, reading them from .github/rulesets/default.json
# and .github/labels.json so the repo's own files stay the source of truth.
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
# `strict_required_status_checks_policy` is on, so a branch must be current
# with `main` before it merges. A run is computed against one merge ref, and a
# later merge to the base replaces it, which is how a rollup reads green after
# the branch underneath it has gone stale.

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
# and this file is copied between them.
ruleset_name="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["name"])' "$ruleset_file")"
existing_id="$(gh api "repos/$repo/rulesets" --jq \
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
echo "code scanning: CodeQL default setup"
if ! run gh api --method PATCH "repos/$repo/code-scanning/default-setup" \
  --raw-field state=configured \
  --raw-field query_suite=default \
  --raw-field threat_model=remote \
  --raw-field 'languages[]=actions' \
  --raw-field 'languages[]=python' >/dev/null 2>&1; then
  echo "  could not configure CodeQL. It needs code pushed and a language" >&2
  echo "  GitHub recognises, so re-run this script after the first push." >&2
fi

# --- Reserved human steps ----------------------------------------------------
cat <<'NOTES'

Done. Three steps stay with a human, because nothing here can guess them.

1. Milestones. Create one per slice, named as docs/build-plan.md names them.
   A filed issue needs a milestone or it appears in no slice view.
2. The premise. Fill the slot at the top of CLAUDE.md and the premise section
   in docs/design.md. Every ranking decision appeals to it, so it comes first.
3. The package name. Rename src/project/ and update the `packages` entry in
   pyproject.toml to match.
NOTES
