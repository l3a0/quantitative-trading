---
name: update-build-board
description: Update the Quantitative Trading Build Board artifact whenever work on this repo changes what it shows. Run it when a decompose loop exits, when a pull request opens or merges, when a review lands on one, and when issues are filed or closed, as well as on any request to refresh or sync the board. Needs the Artifact tool. Answering what to take next is a read and does not on its own call for a republish.
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

Five moments, and each is one where the page's own answer changed. A session
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

A branch that closes no issue gets no card at all, because the page is built
from the tracker. That has happened, and the fix was to file the issue and link
the branch to it rather than giving the page a second source of truth. Check
`closingIssuesReferences` when a pull request opens, and if it is empty and the
branch means to close something, fix the body before the board is touched.

One block these five do not maintain, said plainly rather than left to be
discovered. `WORKING` marks a card a session is on right now, which is only
knowable while a session is running, and every moment above fires when one
finishes. So the Building column reads zero unless something outside this skill
writes that array, and a stale entry in it has nothing to clear it. Treat an
entry as owed a removal by whoever added it, and read an empty Building column
as no information rather than as nobody working.

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
root**, not from the scratch directory the rest of this page works in. Five of
them fail loudly there and one does not: `uv run pytest` reports `no tests ran`,
which looks enough like a result to be written down.

A count recalled from earlier in the session is the one that will be wrong, and
it has been: an update shipped 39 open issues when a query said 40.

```bash
git fetch --prune origin && git log --oneline -1 origin/main
gh issue list --state open --limit 100 --json number --jq 'length'
gh pr list --state open --json number,title,mergeable,statusCheckRollup,closingIssuesReferences
uv run pytest -q --no-header 2>&1 | tail -1
python3 -c "import json;print(sum(json.loads(l)['row_count'] for l in open('data/vintages.jsonl')))"
wc -l < data/vintages.jsonl
grep -c 'Location' research/book-notes/quantitative-trading.md
gh issue list --state open --limit 100 --json number,labels --jq 'sort_by(.number)[]|"\(.number)\t\(.labels|map(.name)|join(","))"'
```

`wc -l` on the manifest is `vintages.files`, and the line above it is
`vintages.rows`.

The last command feeds every card's `labels`. They are the tracker's own labels
rather than a second vocabulary, so a label added on GitHub belongs on the card,
and `LABEL_HUE` takes its colour from `gh label list --json name,color`.

Two hues are deliberately not GitHub's, and the rule is readability rather than
fidelity. A label colour on GitHub is a chip background, while here it is text,
so a value that reads fine there can be invisible here. `enhancement` is
`a2eeef` and `deferred` is `ededed`, both too pale to read as text on white, so
the page substitutes a darker colour for each. Syncing `LABEL_HUE` straight from
the command would undo both.

That last one is `notes.highlights`. The one figure with no command is
`issues.tracked`, the count of experiments the sibling experiments page lists,
which moves only when that page does. Leave it alone rather than deriving it
from the open issue count, which is a different number and has been confused
with it before.

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

The middle command is why `reviewed` is counted rather than queried today, and
the constraint is what this session posts rather than anything about the API. A
review posted with `gh pr comment` is an issue comment, which never reaches
`reviews` or moves `reviewDecision`, so a landed review and an unwritten one are
indistinguishable by query. `gh pr review --comment` posts a review instead, and
an author may leave one on their own pull request even though they may not
approve it. If a session posts reviews that way, `reviewed` becomes queryable
and the comment count stops being needed. Until then, count the comments that
open with a review heading, because that flag is the only thing that moves a
card into the column saying the next move is the owner's.

Read the checks against the pull request's current head, because a rollup is a
claim about one merge ref at one moment and goes stale in both directions.

Read `status` before `conclusion`. An in-progress run carries a null conclusion,
so anything that tests for "not success" reads it as a failure, and only a
completed run's conclusion means anything. The board's own `checkword` does it
that way. This is a fourth rollup behaviour alongside the three `CLAUDE.md`
already lists, and it belongs there rather than only here, which
[issue 87](https://github.com/l3a0/quantitative-trading/issues/87) carries.

## The data blocks, and what each owns

Everything the page says comes from two objects and six arrays in its script.
They are not adjacent: `STATE`, `PRS`, `WORKING`, `PLANNED` and `NEXT` sit
together near the top, `TRACKER` is about a third of the way down, and `FLOW` is
near the bottom beside the code that reads it. Find each by name rather than by
scrolling. Change the data. Never hand-write a sentence stating a number the
data already carries, because that sentence outlives the number.

| Block | Holds |
| --- | --- |
| `STATE` | `main`, `updatedAt`, `vintages`, `suite.tests`, `notes.highlights`, `issues.open`, `issues.tracked` |
| `PRS` | per pull request: `pr`, `issue`, `state`, `linked`, `reviewed`, `review`, `rollup` |
| `WORKING` | cards a session is on now: `n`, `kind` of `build` or `decompose`, and `what`, a phrase rendered on the card |
| `PLANNED` | cards whose decompose loop exited: `n`, `passes`, `ready`. A `note` is carried for the next editor and is not rendered |
| `TRACKER` | every open issue as a card: `n`, `ms`, `labels`, `needs`, optional `after`, `kind`, `label` |
| `NEXT` | the priority order, each keyed by `issue` rather than `n`, with `band`, `ready`, `title`, `why`, and an optional `order`. It renders no section of its own. It drives the sort inside every column and the small number chip on the cards it names |
| `FLOW` | the four in-flight stages and the test that assigns a card to one |
| `LABEL_HUE` | one colour per tracker label, read by the card chips |

Three of these carry judgement rather than measurement, so they are where the
thinking goes.

1. **`needs` against `after`.** `needs` is a hard blocker and moves a card into a
   deeper column. `after` is an ordering somebody measured that nothing
   enforces, so it leaves the card where it is and sorts it below what it names.
   Issue 2 carries `after: [41]` because a default Windows clone goes from two
   red tests to twenty-nine if they land the other way round. Using `needs`
   there would have said something false.
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
// unnoticed, so the sweep is what guarantees the list cannot go stale.
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
5. **Every conjunction still has its other half.** A computed sentence joins
   clauses that each drop out on their own, so a "too" or an "and" can outlive
   the clause it referred back to. One read "#27 is planned too" with nothing
   before it, because the card it was agreeing with had merged. Read the
   sentences, not only the counts.
6. **Nothing a card says contradicts where the card sits.** A marker, a line of
   text and a position are three claims about one issue, and a rule added to any
   of them can disagree with the other two. A chip once read 6 on a card the sort
   had forced to the bottom. Read each card's own marks against its place in the
   column.

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
   advertising states that had moved to another section. It came back computed,
   which was not enough: after defect 11 landed, the in-flight legend still
   offered "ready to hand to a builder" for a card whose pull request had
   retired that marker, because it computed from `PLANNED` rather than from what
   was drawn. Both spellings fail the same way. A legend reads the render.
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
11. **A plan line under a pull request.** A card with an open branch said its
    plan was ready to be written, directly above a line saying it was written.
    The plan line and its marker are suppressed once a pull request exists,
    while the sort still reads `PLANNED` so the card keeps its position. Two
    things follow. The suppression is specific to that pair rather than a licence
    to hide other states. And suppressing a marker splits the render from the
    data, so every other reader of the same field has to be swept: the legend was
    missed, which is the second half of defect 6.
12. **Two fixes that each worked, contradicting each other.** A priority chip
    was added to the cards when the ranking section was deleted, and separately
    the sort was changed to force a deferred card last because one had been
    sitting fourth in a column of twenty-five. Together they gave issue 10 a
    chip reading 6 above a position reading last, which is two answers to one
    question. The chip is dropped on a deferred card, because the ranking holds
    one only to record that it is deliberately not being done, and the dashed
    border and the kind word already say that. The shape is not rare: the card
    renderer carries two other comments reasoning about giving one card two
    answers to one question. Check 6 below is what catches the next one, so a
    rule added to a card is read against the card's own position rather than
    only against the data it came from.

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

Publish, then report in the same reply.

1. The version number and what moved.
2. Any sentence the execution caught, and what replaced it.
3. What is still stale, including the two sibling pages.

If a publish is refused because the artifact moved, do not force it. Read the
live version, merge onto it, and publish again. Forcing discards somebody's work.

This has fired once, since the update became every session's job. The refusal
hands over the live source. Read all of it, and decide which side is newer part
by part rather than for the file as a whole, because the two can differ: that
time the other session had improved the rendering code while this one held newer
measurements, so the data moved onto their file. Resending a file unchanged
reverts whatever the other session did.
