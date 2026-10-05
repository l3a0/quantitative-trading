---
name: sync-prune-next
description: Sync with origin, prune the worktrees and branches whose work is finished, refresh the build board, and recommend what to take next. Use when asked to "git sync prune", to clean up worktrees or branches, to "update the build board and say what's next", or for any status round of this repo's sessions and pull requests.
---

# Sync, prune, and say what's next

Many sessions work on this repo at once, each in its own worktree, so the
checkout fills with worktrees and branches whose work has merged. Removing them
keeps the list readable. Removing the wrong one loses work nobody pushed, and
that cannot be recovered. So most of this skill is about telling the two apart
from evidence rather than from a branch name or a session title.

The round has four steps, and they run in this order because each feeds the
next.

1. Fetch and prune, so every later check reads the current `main`.
2. Remove what is finished, and only that.
3. Update the build board.
4. Recommend what to take next.

## 1. Fetch and prune

```bash
git fetch --prune origin && git log --oneline -6 origin/main
git worktree list
git branch --format='%(refname:short) %(upstream:track)'
```

The log shows what merged since the last round, which is what moves the board
and what can make a Substack draft stale.

Fast-forward the main checkout only when it is clean, since it may belong to a
session too.

```bash
cd "$(git worktree list | head -1 | cut -d' ' -f1)" && [ -z "$(git status --porcelain)" ] && git merge --ff-only origin/main
```

## 2. Remove what is finished, and only that

A worktree or branch is removable only when all four of these hold.

1. **No session is running in it.** `list_sessions` reports `isRunning` and the
   `cwd` and `branch` of every session. A running session's worktree and branch
   stay, whatever else is true.
2. **Its commits are already safe.** Either the branch is an ancestor of
   `origin/main`, or its head equals the `headRefOid` of a merged pull request.
   Squash merges make the second case common: the branch's commit never reaches
   `main`, but the pull request's head records it.
3. **The worktree has no uncommitted changes.** `git status --porcelain` is
   empty.
4. **It is not locked by a live process.** `git worktree list --porcelain`
   prints `locked` with a pid for a sub-agent's worktree. If `ps -p <pid>`
   finds the process, the agent is still working.

`isRunning: false` does not mean a session has ended. A session waiting on its
own background sub-agents reports it too, which is why the first check cannot
stand alone. On 2026-10-05 the session building
[#335](https://github.com/l3a0/quantitative-trading/issues/335) reported
`isRunning: false`, and its branch sat at `main` with no commits of its own.
Its worktree held seven modified files. Minutes later it opened
[PR #369](https://github.com/l3a0/quantitative-trading/pull/369) from that
branch, and the files turned out to be review fixes in progress. Judged by
session and branch alone, the worktree was safe to delete. The third check is
what kept it.

The same evidence does not show that work has stalled. Before reporting a
session as stuck, re-run `gh pr list --state open` and read its latest events
with `list_events`, because a pull request may have opened since the branch
was classified.

A session that is not running but has an open pull request keeps its worktree,
because review fixes land there.

Classify every branch in one pass. Run the loop under `bash`, since zsh does not
split `$h` into words.

```bash
bash -c 'for b in $(git branch --format="%(refname:short)" | grep -v "^main$\|^(HEAD"); do
  ahead=$(git rev-list --count origin/main..$b)
  inmain=$(git merge-base --is-ancestor $b origin/main && echo inmain || echo -)
  pr=$(gh pr list --state all --head $b --json number,state,headRefOid --jq ".[]|\"\(.number):\(.state):\(.headRefOid[0:7])\"" | tr "\n" " ")
  echo "$b $(git rev-parse --short $b) ahead=$ahead $inmain pr=[$pr]"
done'
for w in $(git worktree list --porcelain | sed -n "s/^worktree //p"); do
  echo "$w dirty=$(git -C "$w" status --porcelain | wc -l | tr -d " ")"
done
```

Then remove with the commands that refuse to lose work. `git worktree remove`
without `--force` refuses a dirty tree, and that refusal is a check worth
keeping. Use `git branch -D` only on a branch the classification showed is
`inmain` or matches a merged pull request's head.

```bash
git worktree remove <path>
git branch -D <branch>
git worktree prune
```

Archive a finished session only when the owner has asked for it in this
conversation. Archiving stops the session and is the owner's call, even when the
board says its loop exited.

Report what was removed, and what was kept with the reason for each. The kept
list is where the owner learns about work in progress that nothing else
announces, such as the dirty worktree above.

## 3. Update the build board

The `update-build-board` skill owns the procedure, the data blocks and the
checks, so this step only names what a round usually changes.

- `PRS` takes each open pull request's checks at its current head, counts its
  `## Review` comments, and drops pull requests that merged or closed.
- `TRACKER` and `STATE.issues.open` take issues filed or closed since the last
  round. The count of cards must equal the open issue count.
- `WORKING` loses entries whose session ended. The session list says which.
- `STATE.main`, `suite.tests` and the two vintage counts wait for one suite run
  on a clean checkout of the new `main`, and go in a single pinned write.

The suite takes six to nine minutes, so start it in the background as soon as
`main` has moved, and write everything else without waiting for it.

```bash
D=$(mktemp -d) && git worktree add -q --detach "$D" origin/main && (cd "$D" && git log --oneline -1 && uv run pytest -q --no-header 2>&1 | tail -1 && wc -l < data/vintages.jsonl && python3 -c "import json;print(sum(json.loads(l)['row_count'] for l in open('data/vintages.jsonl')))"); git worktree remove --force "$D"
```

`--force` is safe here because the worktree is a fresh checkout made by this
command, and the suite's caches are all it can leave behind.

## 4. Recommend what to take next

The ranking directive in `CLAUDE.md` decides the order. Collect candidates from
four places, and give the evidence for each one.

1. **The owner's queue.** These are pull requests with a review and green
   checks, `PLANNED` entries with `ready` of `decide`, and questions a session
   handed back. Nothing moves until the owner answers, so they come first.
2. **Plans ready to build with no builder.** These are `PLANNED` entries with
   `ready` of `build` and no `WORKING` entry and no open pull request.
3. **Blog drafts.** List the Substack drafts and their schedule. A merged or open
   pull request that touches `blog/` makes its draft stale, and syncing it needs
   the owner's approval. The draft ids live outside this repo, in Claude's
   local memory for it.
4. **The replication backlog**, in the tracker's order, for when nothing above
   is waiting.

Link every issue and pull request number. Say which candidates only the owner
can act on, and which a new session can start without them.
