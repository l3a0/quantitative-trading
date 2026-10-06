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
```

The log shows what merged since the last round, which is what moves the board
and what can make a Substack draft stale.

`--prune` drops a remote-tracking ref only when its branch was deleted on
GitHub, and this repo does not delete a branch when its pull request merges. So
remote branches pile up. Deleting them is the owner's call, and this skill
leaves them alone.

Fast-forward the main checkout only when it is clean and on `main`, since a
session may be using it. `git -C` keeps the shell where it is, which matters
because the Bash tool keeps a `cd` for every later command.

```bash
M=$(git worktree list | head -1 | cut -d' ' -f1)
[ "$(git -C "$M" branch --show-current)" = main ] && [ -z "$(git -C "$M" status --porcelain)" ] && git -C "$M" merge --ff-only origin/main
```

## 2. Remove what is finished, and only that

A worktree is removable only when all five of these hold.

1. **It is not the worktree this round runs in.** `list_sessions` leaves out
   the current session, so nothing else protects it, and git removes a worktree
   from inside it without complaint. Compare against
   `git rev-parse --show-toplevel`.
2. **No unarchived session has it as its `cwd`.** Read `cwd`, not `branch`.
   `branch` is the branch a session started on, and a session that switched
   branches reports one it no longer uses. Read `isRunning` as no evidence
   either way. An open session between turns reports `false`, and so does one
   waiting on its own background sub-agents. Pass a `limit` above the default
   of 20 so no session is missed.
3. **Its `HEAD` commit is safe.** Test the worktree's `HEAD` itself, not only
   its branch, because a worktree with no branch checked out holds commits that
   no branch names. The commit is safe when `origin/main` contains it, when a
   remote branch contains it (`git branch -r --contains`), or when it equals
   the `headRefOid` of a merged pull request. Squash merges make the last case
   common, because the branch's commit never reaches `main`. Test that last case
   by exact comparison against the list of merged heads. A
   `gh pr list --search <sha>` matches any commit inside a pull request, not
   only its head, so it does not test what this check states. `61f8892`
   matched [PR #414](https://github.com/l3a0/quantitative-trading/pull/414),
   whose head is `ab9be84`.
4. **It holds no uncommitted changes.** `git status --porcelain` is empty.
   That listing omits ignored files, which `git worktree remove` deletes
   silently. `--ignored` shows them. Caches such as `.venv/` and
   `.pytest_cache/` are expected, and anything else is a reason to keep the
   worktree.
5. **It is not locked.** `git worktree list --porcelain` prints `locked` with a
   reason for a sub-agent's worktree. The pid in that reason belongs to the
   host session's `claude` process, not to the agent, so a live pid shows only
   that the host is alive. Leave a locked worktree alone. If its pid is gone and
   the other checks pass, `git worktree unlock` it first, because
   `git worktree remove` refuses any locked worktree.

`isRunning` cost something once already. On 2026-10-05 UTC the session
building [#335](https://github.com/l3a0/quantitative-trading/issues/335)
reported `isRunning: false`, and its branch sat at `main` with no commits of
its own. Its worktree held seven modified files. Minutes later it opened
[PR #369](https://github.com/l3a0/quantitative-trading/pull/369) from that
branch, and the files turned out to be review fixes in progress. Check 4 is
what kept the worktree.

The same evidence does not show that work has stalled. Before reporting a
session as stuck, re-run `gh pr list --state open --limit 1000` and read its
latest events with `list_events`, because a pull request may have opened since
the worktree was classified.

Check 3's last case needs the heads of the merged pull requests. Fetch them
once into a file, so both loops below read the same list. A shell variable
would not reach the second loop, because each Bash tool call starts a new
shell. Replace `<scratch>` with the scratch directory in this block and the two
after it.

```bash
MERGED="<scratch>/merged-heads.txt"
gh pr list --repo l3a0/quantitative-trading --state merged --limit 1000 --json headRefOid --jq '.[].headRefOid' > "$MERGED"
wc -l < "$MERGED"
```

A count of exactly 1000 means `gh` cut the list, so raise the limit and fetch
again.

This prints what checks 3 to 5 need for every worktree.

```bash
MERGED="<scratch>/merged-heads.txt"
git worktree list --porcelain | sed -n 's/^worktree //p' | while read -r w; do
  if ! h=$(git -C "$w" rev-parse HEAD 2>/dev/null) || [ "$(git -C "$w" rev-parse --show-toplevel 2>/dev/null)" != "$w" ]; then
    echo "$w unreadable, skipped"; continue
  fi
  safe=$( { git merge-base --is-ancestor "$h" origin/main && echo main; } || git branch -r --contains "$h" | head -1 | tr -d ' ')
  grep -qxF "$h" "$MERGED" && safe="$safe merged-pr-head"
  echo "$w head=${h:0:7} branch=$(git -C "$w" branch --show-current) safe=[${safe}] dirty=$(git -C "$w" status --porcelain | wc -l | tr -d ' ') ignored=$(git -C "$w" status --porcelain --ignored | grep -c '^!!')"
done
git worktree list --porcelain | grep -B3 '^locked'
```

A worktree printed as unreadable has a directory that is gone or a `.git` file
that is broken. Its `HEAD` cannot be read, so none of the tests can pass for
it, and the loop skips it rather than test an empty commit. Report it as kept.
Before this guard, an empty `HEAD` reached `gh pr list --search ""`, which
returns the newest merged pull request, so the line called an unchecked
worktree safe.
The `--show-toplevel` comparison catches a quieter case. The worktrees sit
inside the main checkout, so a worktree directory with no `.git` file at all
resolves to the main checkout, and without the comparison it reports the main
checkout's `HEAD` as its own.

A branch checked out in no worktree is removable when check 3 holds for its
head. Git refuses to delete a branch that a worktree has checked out, which
protects every branch in use. This loop runs the same three tests as the one
above. Matching on the branch name instead, with `gh pr list --head <branch>`,
finds a pull request only when the local branch name equals the one it was
pushed under.

```bash
MERGED="<scratch>/merged-heads.txt"
git branch --format='%(refname:short)' | grep -v -e '^main$' -e '^(HEAD' -e '^(no branch' | while read -r b; do
  h=$(git rev-parse "$b")
  safe=$( { git merge-base --is-ancestor "$h" origin/main && echo main; } || git branch -r --contains "$h" | head -1 | tr -d ' ')
  grep -qxF "$h" "$MERGED" && safe="$safe merged-pr-head"
  echo "$b ${h:0:7} ahead=$(git rev-list --count origin/main.."$h") safe=[${safe}]"
done
```

When the loop runs from a worktree with no branch checked out, `git branch`
adds a line for that worktree's `HEAD`. The line usually reads
`(HEAD detached at <sha>)`. It reads `(no branch)` instead when the `HEAD`
reflog does not record the detach, and `(no branch, rebasing <branch>)` during
a rebase. The `^(HEAD` pattern misses both, so the third pattern removes them.

Write one `-e` per pattern rather than joining them with `\|`. macOS's
`/usr/bin/grep` reads the `$` before `\|` as a literal character, so the joined
form keeps `main` in the list, and `main` then reads as safe to delete.

Then remove with the commands that refuse to lose work. `git worktree remove`
without `--force` refuses a worktree holding modified or untracked files, and
that refusal is a check worth keeping. Use `git branch -D` only on a branch
whose head passed check 3.

```bash
git worktree remove <path>
git branch -D <branch>
git worktree prune
```

Archive a finished session only when the owner has asked for it in this
conversation. Archiving stops the session and is the owner's call, even when the
board says its loop exited.

Report what was removed, and what was kept with the reason for each. Include
stash entries from `git stash list`, which survive every removal above and
which nothing else surfaces. The kept list is where the owner learns about work
in progress that nothing else announces, such as the worktree above.

## 3. Update the build board

The `update-build-board` skill owns the procedure, the data blocks and the
checks, including the reconcile check on the totals. This step
only names what a round usually changes.

- `PRS` takes each open pull request's checks at its current head and its
  `## Review` count, and drops pull requests that merged or closed.
- `TRACKER` and `STATE.issues.open` take issues filed or closed since the last
  round. `PLANNED` and `NEXT` drop entries for closed issues.
- `WORKING` entries are owed a removal by whoever added them, so report a stale
  one rather than deleting another session's entry. A build session keeps its
  entry until it hands its pull request over, so an entry on a card with an
  open pull request keeps that card out of the owner's queue whatever its
  `kind`. Ask whoever added it before calling it stale.

Nothing in a round waits on a suite run. The board stopped carrying the commit,
the test count and the vintage counts on 2026-10-05 UTC, so every section is
written as soon as it is measured.

## 4. Recommend what to take next

The ranking directive in `CLAUDE.md` decides the order, and the board's `NEXT`
block stores it, so read `NEXT` rather than re-deriving it. Collect candidates
from four places, and give the evidence for each one.

1. **The owner's queue.** Nothing moves until the owner answers, so these come
   first.
   - Pull requests that are reviewed, green at the current head, and carry no
     `WORKING` entry on their card.
   - `PLANNED` entries with `ready` of `decide`.
   - Questions a session handed back.
2. **Plans ready to build with no builder.** These are `PLANNED` entries with
   `ready` of `build`, with no `WORKING` entry and no open pull request.
3. **Blog drafts.** List the Substack drafts and their schedule. A merged or open
   pull request that touches `blog/` can leave its draft stale, and syncing it
   needs the owner's approval. A pull request's own session may already have
   synced it, so compare before asking. The draft ids live outside this repo,
   in Claude's local memory for it.
4. **The replication backlog**, in `NEXT`'s order, for when nothing above is
   waiting.

Link every issue and pull request number. Say which candidates only the owner
can act on, and which a new session can start without them.
