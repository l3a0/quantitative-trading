---
name: update-build-board
description: Update the Quantitative Trading Build Board artifact whenever work on this repo changes what it shows. Run it when a decompose loop exits, when a pull request opens, merges, closes unmerged or gains a review, when its checks settle, and when an issue is filed, closed, retitled or relabelled, as well as on any request to refresh or sync the board. Needs the Artifact tool. Answering what to take next is a read and does not on its own call for a republish.
---

# Update the build board

The board is a private artifact at `https://claude.ai/artifact/XzAe2ETdBs4NRCob7kqdJW`.
It cannot read the disk or poll GitHub, so every number on it was measured by
hand and baked in. That is why this skill exists. A page that cannot refresh
itself goes wrong silently, and the only thing between it and a confident lie is
the procedure below.

Two sibling pages are not covered here. The experiments page is
`9eXVcuzxSpqi6S3kBQbwgc` and the gap ledger is `YZHWFfB7AiqrwcaK7F7SCS`. Report
them as stale rather than updating them unasked.

## When to run it

Seven moments, and each is one where the page's own answer changed. A session
that hits one and leaves has made the board wrong, and nothing else notices.

1. **A decompose loop exits.** Add the card to `PLANNED` with its pass count and
   whether it is ready to build or waiting on an owner call.
2. **A pull request opens or merges.** An open one moves the card out of the
   build order into the in-flight section, as a `PRS` entry. A merged one
   usually takes the card off the page, because the issue it closed is closed.
3. **A review lands on a pull request.** Set `reviewed` on its `PRS` entry. That
   flag is the only thing that moves a card from waiting on a reviewer to
   waiting on the owner, and it is the column the owner reads first.
4. **An issue is filed or closed.** That moves `TRACKER` and
   `STATE.issues.open`, and it is worth an update on its own.
5. **A pull request closes unmerged.** In-flight membership asks whether a
   `PRS` entry has `state` of `open`, so nothing removes a card on its own and
   it sits in a review column indefinitely.
6. **A pull request's checks settle.** `rollup` is per check, and the footer
   warns that it decays. `CLAUDE.md` already makes a session watch its checks
   after pushing, so the outcome is always known and only writing it down is
   optional.
7. **An issue is retitled or relabelled.** `TRACKER` carries `label`, `ms` and
   `labels` by hand, and none of them moves on its own. A decompose loop
   correcting a body counts under the first moment only if the loop exits.

A branch that closes no issue gets no card at all, because the page is built
from the tracker. That has happened, and the fix was to file the issue and link
the branch to it rather than giving the page a second source of truth. Check
`closingIssuesReferences` when a pull request opens, and if it is empty and the
branch means to close something, fix the body before the board is touched.

One block these seven do not maintain, said plainly rather than left to be
discovered. `WORKING` marks a card a session is on right now, which is only
knowable while a session is running, and every moment above fires when one
finishes. So the Building column reads zero unless something outside this skill
writes that array, and a stale entry in it has nothing to clear it. Treat an
entry as owed a removal by whoever added it, and read an empty Building column
as no information rather than as nobody working.

Whoever adds an entry sets its `kind`, because that field decides whether the
card keeps its plan marker. A build session writes `build` and a decompose loop
writes `decompose`, and an entry carrying no `kind` counts as a decompose loop.
So a build session that leaves it out puts a line reading ready to build on a
card somebody is already building, which is defect 11 arriving through the
default rather than through a rule.

## What the page is made of

A header strip and three sections, top to bottom. The strip is where every
`STATE` figure renders: `main`, the vintages and their rows, the highlight
count, the test count, the experiments tracked, the open issue count and the
stamp. The sections are these.

1. **In flight**, four columns running most finished on the left: waiting on
   your review, waiting on my review, building, planned with no builder. A card
   here is drawn once and left out of the build order.
2. **Build order**, four columns by dependency depth, with everything else.
   Within a column, cards sort by readiness, then by the priority order, then by
   a measured `after`, then by number, except that a card whose `kind` is
   `deferred` is forced last whatever the rest says. Under it sits a chainbar,
   which holds a hint until a card is picked and then says what that card waits
   on and what waits on it.
3. **One paragraph**, saying the page was measured by hand and cannot poll
   anything. It is all that remains of a twenty-paragraph footer that was a
   second telling of what the cards say. Do not grow it back.

## Read the live artifact before editing anything

Another session may have republished since this one last saw the page, and a
publish over a version nobody read is refused. A copy sitting in a scratchpad is
a guess about what is published.

```text
Artifact action="read" url="https://claude.ai/artifact/XzAe2ETdBs4NRCob7kqdJW"
```

Save what comes back to a scratch file. The rest of this page calls it
`qt-board.html` and works in a scratch directory rather than the repo root,
because the verification step writes two intermediate files and neither belongs
in a commit. Edit that copy, then publish it with the same `url`, which keeps
the link, and a short `label` naming the change.

## Measure everything, recall nothing

Every figure on the page has a command behind it. Run them **from the repo
root**, not from the scratch directory the rest of this page works in. Most fail
loudly there. One does not: `uv run pytest` reports `no tests ran` and exits
zero, which looks enough like a result to be written down.

A count recalled from earlier in the session is the one that will be wrong, and
it has been: an update shipped 39 open issues when a query said 40.

**Run the suite against the commit the strip names, on a checkout of it.** Not
in whichever worktree the session happens to be standing in, which is rarely
`main`. An update published 243 tests beside `2938775`, where the real count was
241, because the run happened in a branch that adds tests. The strip prints the
count next to the commit, so a figure from another tree is attributed to a tree
that never produced it. `git worktree add --detach <dir> origin/main` gives a
clean one, and removing it afterwards is part of the same step.

That one is worth reading twice, because its cover story arrived on its own. PR
90 merged twenty minutes later and made 243 right for `main`, so a session
checking the number afterwards would have found it correct and left the method
that produced it in place.

```bash
git fetch --prune origin && git log --oneline -1 origin/main
gh issue list --state open --limit 100 --json number --jq 'length'
gh pr list --state open --json number,title,statusCheckRollup,closingIssuesReferences
uv run pytest -q --no-header 2>&1 | tail -1
python3 -c "import json;print(sum(json.loads(l)['row_count'] for l in open('data/vintages.jsonl')))"
wc -l < data/vintages.jsonl
grep -c 'Location' research/book-notes/quantitative-trading.md
gh issue list --state open --limit 100 --json number,labels,milestone --jq 'sort_by(.number)[]|"\(.number)\t\(.milestone.title)\t\(.labels|map(.name)|join(","))"'
```

`wc -l` on the manifest is `vintages.files`, and the line above it is
`vintages.rows`. The `grep` is `notes.highlights`. The one figure with no
command is `issues.tracked`, which counts the experiments the sibling
experiments page lists and moves only when that page does. Leave it alone rather
than deriving it from the open issue count, which is a different number and has
been confused with it before.

The `gh issue list` command feeds every card's `ms` and `labels`. `ms` is the
GitHub milestone title, printed on the card exactly as the tracker spells it,
which is why it is queried rather than recalled from the five that exist. They are the tracker's own labels
rather than a second vocabulary, so a label added on GitHub belongs on the card,
and `LABEL_HUE` takes its colour from `gh label list --json name,color`.

Two hues are deliberately not GitHub's, and the rule is readability rather than
fidelity. A label colour on GitHub is a chip background, while here it is text,
so a value that reads fine there can be invisible here. `enhancement` is
`a2eeef` and `deferred` is `ededed`, both too pale to read as text on white, so
the page substitutes a darker colour for each. Syncing `LABEL_HUE` straight from
the command would undo both.

The vintage row count comes from the manifest rather than from counting lines.
All eight files carry three header lines, `Price,Close` then `Ticker,<SYM>` then
`Date,`, so `wc -l` over all eight gives 41,305 against the manifest's 41,281.
The manifest is the authority.

Three things decide where an open pull request's card goes, and none is
guessable.

```bash
gh pr view <n> --json closingIssuesReferences
gh pr view <n> --json comments --jq '[.comments[]|select(.body|startswith("## Review"))]|length'
gh api repos/l3a0/quantitative-trading/commits/$(gh pr view <n> --json headRefOid --jq .headRefOid)/check-runs
```

An empty `closingIssuesReferences` on a pull request that means to close
something is the signal to fix its body before merging, and it is the only way
to tell a plain keyword from one inside a code span. It catches the opposite
slip too: a sentence written to say a pull request closes nothing registered a
link anyway, because the keyword parses wherever it sits.

That query is eventually consistent. On pull request 94 it reported nothing
seconds after the body gained its closing keyword and reported the link on the
next call, so a session that reads it once and acts on the empty result rewrites
a body that was already right. Read it a second time before concluding the
keyword failed.

The middle command is why `reviewed` is counted rather than queried today, and
the constraint is what this session posts rather than anything about the API. A
review posted with `gh pr comment` is an issue comment, which never reaches
`reviews` or moves `reviewDecision`, so a landed review and an unwritten one are
indistinguishable by query. `gh pr review --comment` posts a review instead, and
an author may leave one on their own pull request even though they may not
approve it. If a session posts reviews that way, `reviews` becomes queryable and
the comment count stops being needed. `reviewDecision` still will not move,
because only an approval changes it, so it is not the field to read either way. Until then, count the comments that
open with a review heading, because that flag is the only thing that moves a
card into the column saying the next move is the owner's.

That heading is a convention this command depends on and nothing else states, so
it is stated here: **a session's review comment opens with a line reading
`## Review`.** A review headed anything else counts as zero, and its card sits
in "Waiting on my review" until somebody notices.

Read the checks against the pull request's current head, because a rollup is a
claim about one merge ref at one moment and goes stale in both directions.

Read `status` before `conclusion`. An in-progress run carries a null conclusion,
so anything that tests for "not success" reads it as a failure, and only a
completed run's conclusion means anything. The board's own `checkword` does it
that way. This is a fourth rollup behaviour alongside the three `CLAUDE.md`
already lists, and it belongs there rather than only here, which
[issue 87](https://github.com/l3a0/quantitative-trading/issues/87) carries.

### Measure again immediately before publishing

The figures taken at the start are a claim about the moment the update began,
and an update takes minutes. Both halves of that gap have already cost something
inside one session.

1. **A rollup settled underneath the edit.** Pull request 90 read five checks
   still running on the first pass and six green on the last. Publishing the
   first reading would have said a branch was not ready when it was. The set of
   runs is not fixed either: `CodeQL` had not been created when the first read
   ran, so a session that reads the runs once is reading a set that is still
   growing.
2. **Two pull requests opened during the edit.** Pull requests 91 and 92 did not
   exist when that update started. By the time it was ready to publish they had
   emptied the Building column and moved two cards a whole stage each.

So re-run the volatile commands as the last step before publishing, and publish
what those say rather than what the session opened with. Volatile means the
first command, the open pull request list, every per-branch query, and both
issue commands rather than only the one that counts them. An issue filed
mid-update moves `STATE.issues.open` and owes `TRACKER` a card, so re-reading
the count on its own leaves the page failing check 1. One was filed during the
update this rule came from.

The first command is in that set because it is the one that shows a merge, and a
merge is what moves the four figures left out: `main` itself, the vintages and
their rows, the suite total and the highlight count. Re-running it is what makes
leaving those four alone safe, so excusing them and excusing it together would
have been circular. Two figures are measured by none of this. `updatedAt` is
written by the session rather than measured, and `issues.tracked` moves only
when the sibling experiments page does.

The price is one more round of queries per update. What it buys is a gap of
seconds between the last measurement and the publish rather than a gap the
length of the whole edit. The gap does not close, because editing the data
blocks takes its own time and a figure that moved sends the session back to edit
again.

Nothing re-derives the page's figures after a publish, so whatever is wrong at
that moment stays wrong until the next session runs this. What does read the
page is the owner, and four rows in the record below were found exactly that
way.

## The data blocks, and what each owns

Everything the page says comes from the blocks below. They are not adjacent:
`STATE`, `PRS`, `WORKING`, `PLANNED` and `NEXT` sit together near the top,
`TRACKER` is about a third of the way down, and the rest are near the code that
reads them. Find each by name rather than by scrolling. Change the data. Never
hand-write a sentence stating a number the data already carries, because that
sentence outlives the number.

Two of them hold rendered prose rather than values. `COLS` carries every
build-order column heading and subtitle, and `KINDWORD` carries the phrase a
card prints for its kind. A heading that looks hardcoded in the template is in
one of those.

One more constant is not in the table because nothing should edit it.
`NEXT_SORTED` is `NEXT` put in order, and it is derived on every load.

| Block | Holds |
| --- | --- |
| `STATE` | `main`, `updatedAt`, `vintages`, `suite.tests`, `notes.highlights`, `issues.open`, `issues.tracked` |
| `PRS` | per pull request: `pr`, `issue`, `state`, `linked`, `reviewed`, `review`, `rollup`, and `partOf` where the branch closes nothing on purpose |
| `WORKING` | cards a session is on now: `n`, `kind` of `build` or `decompose`, and `what`, a phrase rendered on the card. `kind` is read rather than decorative, because a build session suppresses the plan marker and a decompose loop does not. An entry carrying no `kind` counts as a decompose loop |
| `PLANNED` | cards whose decompose loop exited: `n`, `passes`, `ready`. A `note` is carried for the next editor and is not rendered |
| `TRACKER` | every open issue as a card: `n`, `ms`, `labels`, `needs`, optional `after`, `kind`, `label` |
| `NEXT` | the priority order, each keyed by `issue` rather than `n`, with `band`, `ready`, `title`, `why`, and an optional `order`. It renders no section of its own. It drives the sort inside every column and the small number chip on the cards it names |
| `FLOW` | the four in-flight stages and the test that assigns a card to one |
| `LABEL_HUE` | one colour per tracker label, read by the card chips |
| `COLS` | the four build-order column headings and their subtitles, which are rendered prose |
| `KINDWORD` | the phrase a card prints for its `kind`, such as "deferred on purpose" |
| `READY_RANK` | the order `build`, `decide` and `plan` sort in, read by the ranking sort |

Three of these carry judgement rather than measurement, so they are where the
thinking goes.

1. **`needs` against `after`.** `needs` is a hard blocker and moves a card into a
   deeper column. `after` is an ordering somebody measured that nothing
   enforces, so it leaves the card where it is and sorts it below what it names.
   Issue 83 carries `after: [51]` because its own body measures the split: three
   of the failures a second download causes belong to issue 51 and the rest do
   not, so it can be built first while the suite stays red until 51 lands. Using
   `needs` there would have said something false. The first card to carry one was
   issue 2, on a measurement about a Windows clone, and both it and the card it
   named have since merged, which is what an `after` is for.
2. **`PLANNED` means a decompose loop exited**, on two consecutive passes that
   asked different questions and found nothing. Not that a body looks thorough.
   Check the issue for the verdict before adding an entry.
3. **`band` in `NEXT`** is priority under this repo's ranking directive. 1 blocks
   other work or risks data that cannot be recaptured, 2 is the reader chain
   everything waits behind, 3 is a sentence wrong where a reader acts on it, and
   5 is deferred on purpose.

## Verify by executing, never by reading

A parse check is not enough, because a comma dropped inside a nested array still
parses. The page has no suite, so running it is the only check there is.

Run it from the scratch directory holding `qt-board.html`, with `$REPO` set to
this checkout.

```bash
python3 -c "
import re,sys
t=open(sys.argv[1]).read()
open('board.js','w').write(re.search(r'<script>(.*?)</script>', t, re.S).group(1))
" qt-board.html
cat "$REPO"/.claude/skills/update-build-board/dom-stub.js board.js > run.js
cat >> run.js <<'JS'
function s(x){return String(x).replace(/<[^>]+>/g," ").replace(/\s+/g," ").trim();}
var o=[];
o.push("STRIP: "+s(store.strip.innerHTML));
store.flow.innerHTML.split('<div class="col f-').slice(1).forEach(function(c){
  var h=c.match(/<span class="t">([^<]+)<\/span><span class="c">(\d+)<\/span>/);
  var ids=(c.match(/data-n="(\d+)"/g)||[]).map(function(m){return "#"+m.match(/\d+/)[0];});
  o.push("flow  "+h[1]+"="+h[2]+": "+(ids.join(" ")||"(empty)"));});
store.board.innerHTML.split('<div class="col k').slice(1).forEach(function(c){
  var h=c.match(/<span class="t">([^<]+)<\/span><span class="c">(\d+)<\/span>/);
  var ids=(c.match(/data-n="(\d+)"/g)||[]).map(function(m){return "#"+m.match(/\d+/)[0];});
  o.push("board "+h[1]+"="+h[2]+": "+ids.join(" "));});
o.push("FLOWNOTE: "+s(store.flownote.innerHTML));
o.push("BOARDNOTE: "+s(store.boardnote.innerHTML));
o.push("KEY: "+s(store.key.innerHTML));
o.push("FLOWKEY: "+s(store.flowkey.innerHTML));
store.foot.innerHTML.split("<p>").slice(1).forEach(function(x,i){
  o.push("FOOT["+(i+1)+"] "+s(x));});
// Anything the page wrote to that the lines above do not format. Listing the
// surfaces by hand is what let `chainbar` go unread and a dead `rank` probe go
// unnoticed, so the sweep is what keeps that list honest. It sees load-time
// `innerHTML` only: not `stamp`, which only a timer writes, not any
// `aria-label`, since the tag-stripper deletes attributes, and not the
// chainbar's picked state, which needs a click. It cannot see code that renders
// nothing either, which is defect 13 and wants a grep rather than a read.
var shown = {strip:1, flow:1, board:1, flownote:1, boardnote:1, key:1, flowkey:1, foot:1};
Object.keys(store).sort().forEach(function(id){
  if (!shown[id]) o.push("OTHER["+id+"] "+s(store[id].innerHTML));});
o.join("\n");
JS
osascript -l JavaScript run.js
```

`osascript -l JavaScript` is JavaScriptCore, and it is what runs this where no
`node` is installed. It is macOS only. Anywhere else, run the same two files
with whatever JavaScript engine is present, because the stub is plain ES5 and
assumes nothing about its host.

Print every surface the page renders into, not the interesting ones. An earlier
version of this harness skipped `foot`, `key` and `flowkey`, and `foot` is the
largest prose block on the page and the one holding the most hand-written
numbers. Planting a false figure in it left the output byte-identical, so the
check could not see the surface it was most needed on.

**Much of the page is dark when `PRS` and `WORKING` are empty**, which is the
state it is in between batches and every time a session opens the first branch
of one. The flow note collapses to a sentence, the flow legend loses two
entries, and the footer's decay clause disappears entirely. That clause is where
check 5's conjunction lives, so on an empty board the sentence it warns about
cannot be read at all. Where a change touches that code, add an entry to `PRS`
in the scratch copy, run the harness, read the output, and take the entry out
again before publishing.

**Read the output rather than checking that it ran.** About half the defects
this page has shipped were sentences that rendered perfectly and said something
false. Six checks catch most of them.

1. **The totals reconcile.** In-flight cards plus board cards equals open issues,
   and every card carries its labels.
2. **No sentence contradicts another.** The free-card list must not name a card
   that a later sentence says nobody should start.
3. **Every count matches its own list.** A sentence saying four cards and then
   naming three is the prose and the data disagreeing.
4. **No figure is typed into a sentence.** Every number the page renders should
   come from the data blocks, so that changing the data changes the page. This
   holds today and did not always: the footer used to carry twenty paragraphs of
   hand-written prose, and one update left four stale figures in it at once.
   Deleting that prose is what made this check cheap, so the thing to watch for
   is prose growing back rather than a surface to re-read.
5. **Every joined sentence says what it means.** A computed sentence joins
   clauses that each drop out on their own, so a "too" or an "and" can outlive
   the clause it referred back to. One read "#27 is planned too" with nothing
   before it, because the card it was agreeing with had merged. A conjunction
   can also be present and be the wrong word: a set of alternatives joined by
   "and" reads as one card doing all of them at once. So read what a joined
   sentence claims rather than only checking that both halves are there, and
   read the sentences rather than only the counts.
6. **Nothing a card says contradicts where the card sits.** A marker, a line of
   text and a position are three claims about one issue, and a rule added to any
   of them can disagree with the other two. A chip once read 6 on a card the sort
   had forced to the bottom. Read each card's own marks against its place in the
   column.

One class the six cannot reach. Every check above reads what the page rendered,
so none of them sees code that renders nothing. Defect 13 is that class, and
what catches it is a grep rather than a read.

## What goes wrong, from the record

Each of these shipped or was caught at the last moment, except where a row says
otherwise. They are written down because the next one will be a variant rather
than something new.

1. **A sentence outliving its data.** A hardcoded "everything in the third column
   waits on the same two issues" survived the column emptying. Compute the
   sentence from the array, including the branch where the array is empty.
2. **A fixed list of reasons.** The note offered three reasons a card might not
   be free, for one card that was simply deferred. Build the list from the cards
   actually present.
3. **Hardcoded indices.** The in-flight note read positions three and two, so
   reversing the columns silently swapped what it said. Walk the columns.
4. **Counting something twice.** A card carrying an open pull request was listed
   as free to pick up, two sentences before the page said nobody should start
   it. Subtract everything already carried, not only the case you remembered.
5. **Two sorts that agree today.** The grid sorted by issue number while the
   ranking sorted by a measured argument, so the page put issue 2 ahead of issue
   41 in one place and behind it in another. There is now one `cardOrder`
   comparator, and every column that draws cards calls it. Keep it that way.
   The ranking section itself is gone, which is defect 9.
6. **A legend describing cards that are not under it.** It began as a fixed list
   advertising states that had moved to another section. Computing it was not
   enough either: after defect 11 landed, the in-flight legend still offered
   "ready to hand to a builder" for a card whose pull request had retired that
   marker.

   The first correction was wrong and is worth recording as wrong, because it
   nearly became a rule. It said a legend reads the render rather than the data,
   which implies the render outranks the data. It does not. The data is the
   source of truth and the marker is a function of the data plus one suppression
   rule, and the defect was that the rule existed in two places. There is now one
   `planMarker` that both the card and the legend call. **A legend calls whatever
   decides the marker, never a second copy of the rule.** That is defect 5 in a
   second place rather than a new kind of failure.

   The inverse shipped too, and it is one rule read the other way. The in-flight
   legend explained a plan marker and a pull request while saying nothing about
   the session marker, which every card in that render was drawing. A legend accounts
   for each marker its own cards drew, and for no marker they did not.
7. **Declaration order.** `planOf` was read by a sort that ran before its
   declaration, which throws on load rather than degrading quietly. The stub
   catches this immediately.
8. **Pluralisation.** `plu` appended a bare letter s, giving a count of passes
   that read "19 passs". It now handles a word already ending in one.
The four below are a different kind of row. Each was caught by the owner reading
the published page rather than by a check, which is what they have in common.
Three had been on the page for a while. The fourth was made and found inside one
session, and it is kept anyway, because what produced it was two rules meeting
rather than one careless edit. They are the failures this page invites and the
ones a harness cannot see.

9. **A second list of the same cards.** The page carried a ranking section
   listing nine cards the build order already drew, so every card had two homes.
   The one recorded consequence is defect 5, where the two sections ordered one
   pair differently. The section is gone and its order drives the grid instead.
   Do not add a list that restates the cards.
10. **Reasoning duplicated onto a card that links to the issue holding it.**
    When the ranking section went, its argument for each position was moved onto
    the cards, and the longest one rendered several times the height of its
    neighbours for text that was already one click away. The argument belongs on
    the issue, and the card carries the position as a number.
11. **A plan line under work already under way.** A card with an open branch
    said its plan was ready to be written, directly above a line saying it was
    written. The owner later made the same call about a build session, which is
    the same handover before a branch exists, so the marker now goes for either.
    The sort still reads `PLANNED`, so the card keeps its position whether or not
    the marker is drawn.

    The suppression is two measured states rather than a licence to hide
    others, and the original wording of this row said so before the second state
    was added. The principle that looks like it generates them, whether the card
    can still be handed to a builder, reaches further than the evidence does. It
    covers a decompose loop as well, which keeps its marker because it revises
    the plan rather than carrying it out. A rule needing an exception written in
    by hand to reach the two known cases is doing more than the evidence asks.
    That carve-out is why `WORKING` carries `kind`.

    A suppression rule is also a second consumer of the field, so it goes in one
    function every reader calls rather than being written out wherever it is
    needed. Writing it twice is what made the legend wrong, which is the second
    half of defect 6.
12. **Two fixes that each worked, contradicting each other.** A priority chip
    was added to the cards when the ranking section was deleted, and separately
    the sort was changed to force a deferred card last because one had been
    sitting fourth in a column of twenty-five. Together they gave issue 10 a
    chip reading 6 above a position reading last, which is two answers to one
    question. The chip is dropped on a deferred card, because the ranking holds
    one only to record that it is deliberately not being done, and the dashed
    border and the kind word already say that. The shape is not rare: the card
    renderer carries two other comments reasoning about giving one card two
    answers to one question. Check 6 above is what catches the next one, so a
    rule added to a card is read against the card's own position rather than
    only against the data it came from.
The last two are a third kind. Both were made and caught inside one session
rather than by the owner reading the page. Defect 14 came from the harness
output. Defect 13 could not, for the reason it records, and came from reading
the script beside it.

13. **Bindings left behind when the sentence they fed moved.** The board note
    once described the cards a session was on. That sentence moved to the
    in-flight note, and nine bindings that computed it stayed, one of them
    building the whole paragraph and assigning it to a variable nothing reads.
    The harness cannot see this, because it prints what the page rendered and
    dead code renders nothing. So when a sentence is deleted or moved, grep the
    script for the names that fed it. A leftover here costs more than ordinary
    dead code, because it is not inert. It is a finished sentence about live
    data, sitting beside a surface that would print it, under a rule that has
    since changed.
14. **A set of alternatives joined with "and".** The board note lists the reasons
    a first-column card is not free, and `andlist` joined them, so it read that a
    card can need a decision rather than a session and be deferred on purpose.
    The reasons are collected from different cards, which is what defect 2 is
    about, so joining them with "and" hands all of them to one card. The join
    now takes its conjunction as an argument, and
    `andlist` and `orlist` are two names for it. Check 5 used to look only for a
    conjunction whose other half had dropped out. This one had its other half
    and was the wrong word, so that check now covers both.

The four figures that argued for deleting the footer were a count of planned
cards, a count of finished plans, an interpolated test total that made an old
pull request look like it shipped a number it did not, and an issue count
attributed to the wrong work. They are named here because they are what a
hand-written surface costs, and because the fix was to remove the surface rather
than to keep checking it.

## Writing the prose

The repo's own writing rules govern the page's prose. Impersonal voice, no first
person, no em dashes or semicolons, short complete sentences, a counted set
written as a list rather than inlined, and the price of a choice named rather
than hidden.

One exception is deliberate and load-bearing. The in-flight column headings say
"Waiting on my review" and "Waiting on your review", and the whole point of
those two columns is whose move it is. Applying the impersonal rule to them
deletes the distinction the section exists to draw. Keep the first and second
person there, and nowhere else.

Two further conventions are specific to this page.

1. **Say what the page cannot know.** The in-flight section is the most
   perishable thing on it, because a session ends without telling anyone and a
   review posted a minute after the stamp still reads as owed. The footer says
   so, and it keeps saying so.
2. **A comment explains why a rule exists, not what the line does.** The script's
   comments carry the measurements behind its choices, which is what stops the
   next session undoing one by accident.

## Which copy wins where this file and the page overlap

Several things are reasoned about twice, once in a comment beside the line it
governs and once here. The duplication is deliberate and its price is named
rather than hidden, because nothing checks the two against each other and the
page lives outside git where no sweep reaches it.

The split is by question. A comment in the script answers why that line is the
way it is, and it is authoritative about the code it sits on, because it travels
with the code through any rewrite. This file answers how to run an update and
what has gone wrong before, and it is authoritative about the procedure and the
record.

So when the two disagree about a mechanism, the comment is right and this file
is what gets corrected. When they disagree about what a session should do, this
file is right. A session changing the page's behaviour updates the comment on
the line it edits, and checks here for a sentence describing the same mechanism.

## Finishing

Re-measure the volatile figures first, under **Measure again immediately before
publishing** above, then publish and report in the same reply.

1. The version number and what moved.
2. Any sentence the execution caught, and what replaced it.
3. What is still stale, including the two sibling pages.
4. A build task for every card left in "Planned, no builder", per the rule below.

### A planned card with no builder is a build task waiting to be offered

The In flight section's last column holds cards whose decompose loop exited and
that nobody is on. That is planning finished and building not started, so a card
sitting there is work that is ready and idle, and the page has no way to move it
on its own.

So an update that leaves a card there offers a build task for it in the same
reply, one per card, rather than reporting the column and stopping. The desktop
app surfaces such a task as a chip the owner starts. Nothing has to happen
first, because a card only reaches that column once a loop has run its plan
against the code, which is the thing a builder would otherwise have to do again.

Two things the offer needs, since a builder reads the issue once at spawn and
reads none of this.

1. **Check what the card waits on before offering it.** The column's test asks
   only whether a plan exists, whether a branch exists and whether a session is
   on it. It never looks at `needs`, so a plan-complete card sitting behind an
   open blocker lands there too, and offering it hands a builder work they cannot
   finish. Read the card's `needs` against the open issues first. No card has hit
   this yet, because every `PLANNED` entry so far has had an empty `needs`, which
   is why the column was built without the test rather than with it.
2. **Carry what the loop found that the issue body does not repeat.** A
   measurement the loop took, the file the change will collide with, and the
   neighbouring issues the builder must not absorb. `PLANNED` carries a `note`
   for exactly this and renders it nowhere, so it reaches a builder only if the
   offer quotes it.

If a publish is refused because the artifact moved, do not force it. Read the
live version, merge onto it, and publish again. Forcing discards somebody's work.

This has fired once, since the update became every session's job. The refusal
hands over the live source. Read all of it, and decide which side is newer part
by part rather than for the file as a whole, because the two can differ: that
time the other session had improved the rendering code while this one held newer
measurements, so the data moved onto their file. Resending a file unchanged
reverts whatever the other session did.
