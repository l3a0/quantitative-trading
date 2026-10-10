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

`--prune` drops a remote-tracking ref once its branch is gone from GitHub.
Since 2026-10-10 GitHub deletes a pull request's branch when the pull request
merges, because the owner turned on the repository's `delete_branch_on_merge`
setting. So a merged pull request's `origin/<branch>` disappears on the next
round, and step 2 cannot lean on it.

The setting does not reach back. The branches of pull requests that merged
before it stay on GitHub, 102 of them on 2026-10-10. Deleting those is the
owner's call, and this skill leaves them alone.

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
   remote branch contains it (`git branch -r --contains`), or when it is one of
   a merged pull request's commits. Squash merges make the last case common,
   because the branch's commits never reach `main`, and deleting the branch on
   merge leaves no remote branch to contain them either. GitHub keeps every
   commit of a merged pull request, so any of them is safe, not only the head.
   That matters for a review lens's worktree detached at an earlier commit of
   the pull request, or a sub-agent's branch left there. On 2026-10-10 GitHub
   deleted the branches of
   [PR #433](https://github.com/l3a0/quantitative-trading/pull/433) and
   [PR #447](https://github.com/l3a0/quantitative-trading/pull/447) as they
   merged. Five sub-agent worktrees here sat at earlier commits of the two,
   such as `d88745a` in the first, whose head is `886754e`. After the next
   prune no remote branch contained them, and a test of the head alone would
   have kept all five.

   Test the last case by exact comparison against the commits GitHub lists for
   each merged pull request. A commit made here on top of one of them is in no
   list, so it stays unsafe, and so does an amended or rebased copy, whose sha
   differs. Do not use `gh pr list --search <sha>` instead. It matches a
   pull request that only mentions the sha in its text. `b27222b`, a commit in
   the sibling repository that this one does not hold, matched five merged pull
   requests here on 2026-10-10.
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

Check 3's last case needs the commits of the merged pull requests. Fetch them
once into a file, so both loops below read the same list. A shell variable
would not reach the second loop, because each Bash tool call starts a new
shell. Replace `<scratch>` with the scratch directory in this block and the two
after it.

```bash
MERGED="<scratch>/merged-commits.txt"
gh api graphql --paginate -f query='query($endCursor: String) { repository(owner: "l3a0", name: "quantitative-trading") { pullRequests(states: MERGED, first: 100, after: $endCursor) { pageInfo { hasNextPage endCursor } nodes { headRefOid commits(first: 250) { nodes { commit { oid } } } } } } }' --jq '.data.repository.pullRequests.nodes[] | .headRefOid, .commits.nodes[].commit.oid' | sort -u > "$MERGED"
wc -l < "$MERGED"
grep -cvE '^[0-9a-f]{40}$' "$MERGED"
```

`gh pr list --json commits` cannot fetch this list. It asks for each commit's
authors too, and on 2026-10-10 GitHub refused the query for exceeding 500,000
possible nodes at any limit of 50 or more. The query above pages through 100
pull requests at a time, so no limit can cut it short. It reads the first 250
commits of each pull request, and prints each head on its own line as well, so
a longer pull request loses only its later commits from the list and never its
head. The longest merged pull request had 70 commits on 2026-10-10.

Every way this fetch can fail leaves the list shorter, and a shorter list only
keeps more worktrees. A failure does not always leave the file empty, though.
When GitHub rejects the query, `gh` writes the error as one line of JSON, and
`--jq` never runs. So the block prints two counts. The first should be in the
hundreds and the second, the lines that are not a full sha, should be 0.
Anything else means the fetch failed, and the loops would then keep every
worktree that is not on `main` or a remote branch.

This prints what checks 3 to 5 need for every worktree.

```bash
MERGED="<scratch>/merged-commits.txt"
git worktree list --porcelain | sed -n 's/^worktree //p' | while read -r w; do
  if ! h=$(git -C "$w" rev-parse HEAD 2>/dev/null) || [ "$(git -C "$w" rev-parse --show-toplevel 2>/dev/null)" != "$w" ]; then
    echo "$w unreadable, skipped"; continue
  fi
  safe=$( { git merge-base --is-ancestor "$h" origin/main && echo main; } || git branch -r --contains "$h" | head -1 | tr -d ' ')
  grep -qxF "$h" "$MERGED" && safe="$safe merged-pr"
  echo "$w head=${h:0:7} branch=$(git -C "$w" branch --show-current) safe=[${safe}] dirty=$(git -C "$w" status --porcelain | wc -l | tr -d ' ') ignored=$(git -C "$w" status --porcelain --ignored | grep -c '^!!')"
done
git worktree list --porcelain | grep -B3 '^locked'
```

A worktree printed as unreadable usually has a directory that is gone or a
`.git` file that is broken. Git cannot reach its files, so check 4 cannot pass,
and the loop skips it rather than test an empty commit. Report it as kept.
Before this guard, an empty `HEAD` reached `gh pr list --search ""`, which
returns the most recently created merged pull request, so the line called an
unchecked worktree safe.
The `--show-toplevel` comparison catches a quieter case. The worktrees sit
inside the main checkout, so a worktree directory with no `.git` file at all
resolves to the main checkout, and without the comparison it reports the main
checkout's `HEAD` as its own. The comparison also flags a worktree registered
under a path whose letter case differs from the one on disk. Nothing is lost
by keeping that one, so it is still reported as kept.

A `fatal:` or `warning:` line from the loop means some check could not run.
A corrupt index, for one, makes `git status` fail and the line print
`dirty=0`. Keep any worktree whose line came with one.

A branch checked out in no worktree is removable when check 3 holds for its
head. Git refuses to delete a branch that a worktree has checked out, which
protects every branch in use. This loop runs the same three tests as the one
above. Matching on the branch name instead, with `gh pr list --head <branch>`,
finds a pull request only when the local branch name equals the one it was
pushed under.

```bash
MERGED="<scratch>/merged-commits.txt"
git branch --format='%(refname:short)' | grep -v -e '^main$' -e '^(HEAD' -e '^(no branch' | while read -r b; do
  h=$(git rev-parse "$b")
  safe=$( { git merge-base --is-ancestor "$h" origin/main && echo main; } || git branch -r --contains "$h" | head -1 | tr -d ' ')
  grep -qxF "$h" "$MERGED" && safe="$safe merged-pr"
  echo "$b ${h:0:7} ahead=$(git rev-list --count origin/main.."$h") safe=[${safe}]"
done
```

When the loop runs from a worktree with no branch checked out, `git branch`
adds a line for that worktree's `HEAD`. The line usually reads
`(HEAD detached at <sha>)`. It reads `(no branch)` instead when the `HEAD`
reflog does not record the detach, which is what `git worktree add --detach`
leaves. It reads `(no branch, rebasing <branch>)` during a rebase and
`(no branch, bisect started on <branch>)` during a bisect. The `^(HEAD` pattern
misses all three, so the third pattern removes them.

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
git worktree prune --dry-run -v
```

Run `git worktree prune` only when that dry run names no worktree the loop
printed as unreadable. Prune deletes git's record of every worktree whose
directory or `.git` file is gone, which is most of what the loop calls
unreadable. That record holds the worktree's `HEAD` and its reflog, and while
it exists git counts that `HEAD` as reachable. Once it goes, an unpushed commit
on a detached `HEAD` there belongs to no branch and no reflog, and `git gc` may
delete it. A branch whose worktree was pruned also loses its protection, so
`git branch -D`, which refused it before the prune, deletes it after. So leave
those records for the owner, and say so in the report.

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
  `## Review` count. A pull request that merged or closed keeps its entry, with
  `state` set to `merged` or `closed`, while its issue stays open, because the
  card still reads it. The entry drops once the issue closes. Moments 2 and 5
  of `update-build-board` say what each kind of entry does to its card.
- `TRACKER` and `STATE.issues.open` take issues filed or closed since the last
  round. `PLANNED` and `NEXT` drop entries for closed issues.
- `WORKING` entries are owed a removal by whoever added them, so report a stale
  one rather than deleting another session's entry. A build session keeps its
  entry until it hands its pull request over, so an entry on a card with an
  open pull request keeps that card out of the owner's queue whatever its
  `kind`. Ask whoever added it before calling it stale.

That skill reads the board's URL from a file on this machine. When the file
names no single URL, or names a board this account cannot reach, it skips the
board and the round says so. Steps 1, 2 and 4
still run. Step 4 then reads the open pull requests, their checks and their
reviews straight from GitHub, ranks by `CLAUDE.md`'s directive rather than by
`NEXT`, and says it had no `WORKING` or `PLANNED` entries to read.

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
     `WORKING` entry on their card. Green does not count when the base moved
     after the last push, as the paragraph after this list explains.
   - `PLANNED` entries with `ready` of `decide`.
   - Questions a session handed back.
2. **Plans ready to build with no builder.** These are `PLANNED` entries with
   `ready` of `build`, with no `WORKING` entry, no open pull request, nothing
   open in `needs`, and no pull request merged with no `Part of`. That last one
   leaves the card only a close by hand, so it is not a candidate.
3. **Blog drafts.** List the Substack drafts and their schedule. A merged or open
   pull request that touches `blog/` can leave its draft stale. A stale draft
   that is neither published nor scheduled is synced rather than asked about,
   under the
   owner's standing approval in `CLAUDE.md`'s
   `## Write-ups and their Substack drafts`. A pull request's own session may
   already have synced it. So first compare the live draft with the copy of it
   recorded at the last sync, and pull any edit the owner made since then into
   the Markdown rather than overwrite it. A change to a published or scheduled
   post stays in the owner's queue, because writing to its draft changes what
   goes out. Publishing, scheduling and sending stay there too. The draft ids
   and the recorded copies live outside this repo, in Claude's local memory for
   it. The `sync-substack` skill carries the procedure for a sync.
4. **The replication backlog**, in `NEXT`'s order, for when nothing above is
   waiting.

A stacked pull request is the usual way a base moves without a push. It is one
built on another pull request's branch rather than on `main`. GitHub's
documentation on deleting branches says that deleting a merged pull request's
branch moves every open pull request built on it onto the merged one's base. No
stacked pull request here has been moved that way by the setting yet, so that
case rests on the documentation rather than on a run. The move starts no CI
run, because the workflow's `pull_request` trigger runs only on GitHub's
default activity types and a base change is not one of them.
[PR #466](https://github.com/l3a0/quantitative-trading/pull/466) shows the
cost. While it sat on
[PR #464](https://github.com/l3a0/quantitative-trading/pull/464)'s branch, only
`docs` and `test` ran, because CodeQL's default setup scans only pull requests
into the default branch or a protected one. Both were green, so the rollup read
green with four checks missing. Its base was moved by hand on 2026-10-10, and
no run started until its next push. This prints when a pull request's base
moved, to compare with its last push.

```bash
gh api repos/l3a0/quantitative-trading/issues/<n>/timeline --jq '.[]|select(.event=="base_ref_changed")|.created_at'
```

Link every issue and pull request number. Name each pull request's tracking
issue beside it, linked, with how the two relate, as in
"[PR #479](https://github.com/l3a0/quantitative-trading/pull/479), which closes
[#352](https://github.com/l3a0/quantitative-trading/issues/352)" or
"[PR #477](https://github.com/l3a0/quantitative-trading/pull/477), part of
[#457](https://github.com/l3a0/quantitative-trading/issues/457)". One that
tracks no issue says "closes no issue". A table of pull requests gets an issue column. Read the
relation from GitHub at report time, from `closingIssuesReferences` and any
`Part of #NN` line in the body, rather than from memory. This holds in step 2's
kept list too, wherever it names a pull request. `CLAUDE.md`'s
`## Writing style` carries the rule. Say which candidates only the owner can
act on, and which a new session can start without them.
