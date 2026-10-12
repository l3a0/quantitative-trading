---
name: update-build-board
description: Keep the Quantitative Trading Build Board true by setting, on GitHub, the labels, links and lines it reads. Run it when a decompose loop starts or exits, when a build session starts on a card or hands its pull request over, when a review is posted, when an issue is filed or its priority or what it waits on changes, and when the page's code changes. A GitHub Action rebuilds the board from GitHub on every change, so nothing here writes the board itself. Answering what to take next is a read of the board's board.json.
---

# Update the build board

The build board is a page answering what is in flight and what to take next.
It lives on GitHub Pages at <https://l3a0.github.io/quantitative-trading/>, and
its page source is checked in beside this skill as `board.html`. A GitHub
Action, `.github/workflows/board.yml`, runs `scripts/build_board.py` on every
issue, comment and pull request change and on a schedule. The script reads
GitHub and writes the six sections the page draws as one `board.json` beside
the page, and no Claude runs at any step.

So a session never writes the board. What a session does is set the judgement
the board reads, on GitHub: a label, a native "blocked by" link, a line in an
issue body, or a line in a comment. The facts GitHub already records, such as
a pull request opening, its checks settling or an issue closing, reach the
board with nothing set by anyone.

Until [issue 533](https://github.com/l3a0/quantitative-trading/issues/533) the
board was a claude.ai artifact whose figures sessions measured by hand and
wrote into its database. That cost about $51 a day in session turns, measured
on [issue 531](https://github.com/l3a0/quantitative-trading/issues/531), and it
missed every change no session saw. That artifact is retired. Nothing writes
it, and it is kept rather than deleted only because each ranked card's `why`
and each plan's `note` exist nowhere else. Do not write to it, and do not
publish this page to it.

## Where the board lives

| What | Where |
| --- | --- |
| The page | <https://l3a0.github.io/quantitative-trading/> |
| Its data | `board.json` beside the page |
| What builds the data | `scripts/build_board.py`, run by `.github/workflows/board.yml` |
| The page's source | `board.html` beside this skill |

The address is public and the same for every machine, so it lives here rather
than in a file on the machine.

A change reaches the page once a run of the Action finishes. A label, a body
edit and a comment each start a run. A "blocked by" link and a sub-issue start
none, because GitHub Actions lists no trigger for either, so they wait for the
next scheduled run, at minutes 7 and 37 of each hour. Pages also tells a
browser to cache `board.json` for ten minutes, and the page asks for a fresh
copy every two minutes to get round it.

To read the board, as step 4 of `sync-prune-next` does, build it from GitHub
rather than fetching the published copy, because the build reads GitHub as it
stands rather than as the last run saw it. Run this from the repo root, with a
scratch directory as the output, never the repo.

```bash
python3 scripts/build_board.py build --repo l3a0/quantitative-trading \
  --workflow .github/workflows/board.yml --out <scratch>
```

It prints what it read to the terminal and writes `<scratch>/board.json`. A
run that fails says why and writes nothing, because the script stops on any
read it cannot trust rather than writing a board that reads as correct.

## What a session sets, and when

Each moment below is one where the page's answer changes and nothing GitHub
records on its own says so. A session that reaches one and leaves has made the
board wrong, and nothing else notices.

1. **A decompose loop starts.** Add `working:decompose` to the issue.
2. **A decompose loop exits.** Take `working:decompose` off, and post the
   verdict as a comment carrying one line in this form, alone on its line.

   ```text
   Board verdict: build after 5 passes
   ```

   Write `decide` in place of `build` when the loop ended on a question only
   the owner can answer. The newest such comment wins, so a loop run again
   writes a new one rather than editing the old. A loop with passes and no
   exit writes no verdict, because the card's plan marker means the loop
   exited.
3. **A build session starts on a card.** Add `working:build` to the issue.
   It stays after the pull request opens, because until the hand-over it is
   the only thing on the page saying the branch is still moving.
4. **A session hands its pull request over.** That means the review is
   posted, its fixes are pushed, the checks are green at the current head,
   and nothing more is coming. Take `working:build` off. Until then the card
   stays under "Waiting on my review", whatever its review and checks say.
5. **A review lands on a pull request.** Post it as a comment whose first
   line reads `## Review`. A review headed anything else counts as none, and
   its card sits in "Waiting on my review" until somebody notices.
6. **An issue is filed.** Add `blocked-on-data`, `deferred` or `decision`
   where one applies. These are the labels the board reads for a card's
   `kind`, as the table below says. They are separate from the label
   `CLAUDE.md`'s `## Pull requests` asks every filed issue for, saying what
   kind of work it is, such as `bug` or `documentation`. The card prints
   that one among its labels and decides nothing by it. Add a `band:N` label
   if it joins the priority order, because a card with no band is left out of
   the board's default view. Add a native "blocked by" link for each open
   issue it cannot start before, and a `Board after:` line for an ordering
   nothing enforces.
7. **A card's priority changes.** Move its `band:N` label, and add, change or
   remove its `Board order:` line.
8. **What a card waits on changes.** Add or remove its "blocked by" link.

Nothing else needs setting. A pull request opening, merging or closing, its
checks settling, and an issue closing, retitled or relabelled all reach the
board from GitHub.

Only the owner's comments count, for a verdict as for a review. Anyone can
comment on a public repository, and a stranger's comment would otherwise move
a card. Sessions here run `gh` as the owner, so their comments count. Labels
and links need triage access, so they need no such filter.

The commands, with `<n>` the card's issue and `<b>` the issue it waits on:

```bash
gh issue edit <n> --add-label working:build
gh issue edit <n> --remove-label working:build
gh api --method POST repos/l3a0/quantitative-trading/issues/<n>/dependencies/blocked_by \
  -F issue_id="$(gh api repos/l3a0/quantitative-trading/issues/<b> --jq .id)"
gh api --method DELETE \
  "repos/l3a0/quantitative-trading/issues/<n>/dependencies/blocked_by/$(gh api repos/l3a0/quantitative-trading/issues/<b> --jq .id)"
```

A "blocked by" link takes the blocker's database id, which `--jq .id` reads,
rather than its number. A body line is added by editing the issue's body, and
goes on a line of its own, which is what the script reads.

```text
Board order: 14.5
Board after: #51, #83
```

The order takes a decimal, so a card can go between two others without
renumbering either. A line quoted inside a sentence, a code span or a fenced
code block is not read, and neither is a verdict line in a fence.

A branch that closes no issue gets no card at all, because the page is built
from the tracker. Check `closingIssuesReferences` when a pull request opens,
and if it is empty and the branch means to close something, fix the body
before going further. A pull request into any branch but `main` is the
exception. GitHub reads closing keywords only on a pull request into the
default branch, so a stacked one shows an empty list until its base moves to
`main`. That query is eventually consistent. On
[pull request 94](https://github.com/l3a0/quantitative-trading/pull/94) it
reported nothing seconds after the body gained its closing keyword and reported
the link on the next call, so read it a second time before concluding the
keyword failed.

A session that ends without taking its `working:` label off leaves its card
under "Waiting on my review" or "Building" until somebody removes it. That
fails safe, because it delays a merge rather than inviting one too early. A
label is owed its removal by the session that set it, so report a stale one
rather than removing another session's.

## The data, and where each field comes from

The page loads each section of `board.json` into the variable of the same name
in capitals, so `prs` becomes `PRS`, and the rest of this file uses those
names. Change what GitHub holds. Never hand-write a sentence in the page stating
a number the data already carries, because that sentence outlives the number.

| Section | Field | Comes from |
| --- | --- | --- |
| `STATE` | `updatedAt`, `issues.open`, `staleAfterMinutes` | the time GitHub was read, the open issue count, and twice the longest gap in the workflow's schedule |
| `TRACKER` | `n`, `ms`, `label`, `labels` | each open issue's number, milestone, title and labels, less the board's own `band:N` and `working:` labels, which the page draws as the rank chip and the busy stripe |
| `TRACKER` | `kind` | `parent` for an issue with any sub-issue, then `data` for `blocked-on-data`, `deferred` for `deferred` and `decision` for `decision`, in that order where an issue carries more than one, and `ready` otherwise |
| `TRACKER` | `needs` | the issue's native "blocked by" links, keeping only blockers that are open issues in this repository |
| `TRACKER` | `after` | the issue's `Board after:` line, keeping only open issues |
| `PRS` | `pr`, `issue`, `state`, `linked`, `partOf`, `rollup` | each pull request naming an open issue through a closing link or a line opening with `Part of #N`, with its checks at the current head |
| `PRS` | `reviewed`, `review` | an owner's comment opening with `## Review`. Without one, `review` reads "review in progress" while the card carries a `working:` label, and "no review posted" otherwise |
| `WORKING` | `n`, `kind` | the `working:build` and `working:decompose` labels |
| `PLANNED` | `n`, `passes`, `ready` | the newest owner comment carrying a `Board verdict:` line |
| `NEXT` | `issue`, `band`, `order` | the `band:N` label and the `Board order:` line |
| `NEXT` | `ready` | the card's verdict where it has one, `decide` for a card whose kind is `decision`, and `plan` otherwise |

The page's constants live in its code rather than in the data.

| Constant | Holds |
| --- | --- |
| `FLOW` | the five in-flight stages and the test that assigns a card to one |
| `LABEL_HUE` | one colour per tracker label, read by the card chips. A new label renders in the faint ink until a code change adds its colour |
| `COLS` | the four build-order column headings and their subtitles, which are rendered prose |
| `KINDWORD` | the phrase a card prints for its `kind`, such as "deferred on purpose". A new kind prints no phrase until a code change adds one |
| `READY_RANK` | the order `build`, `decide` and `plan` sort in, read by the ranking sort |

`NEXT_SORTED` is `NEXT` put in order, by band, then order with 50 where a card
has none, then readiness, then number. It is derived on every load.

Three of the fields carry judgement rather than measurement, so they are where
the thinking goes.

1. **`needs` against `after`.** `needs` is a hard blocker and moves a card into
   a deeper column. `after` is an ordering somebody measured that nothing
   enforces, so it leaves the card where it is and sorts it below what it names.
   [Issue 83](https://github.com/l3a0/quantitative-trading/issues/83) once
   carried `after: [51]` because its own body measured the split: three of the
   failures a second download causes belonged to
   [issue 51](https://github.com/l3a0/quantitative-trading/issues/51) and the
   rest did not, so it could be built first while the suite stayed red until 51
   landed. A "blocked by" link there would have said something false. A link
   and the issue's `## Depends on` prose then say the same thing twice. The
   link wins, because it is what the board reads, and the prose keeps the
   reason the wait exists.
2. **A verdict means a decompose loop exited**, on a pass that did not reduce
   the body. Not that a body looks thorough. Read the pass count as a cost
   rather than a depth: one run reached 109 under the older exit rule, which
   asked for two consecutive empty passes and could not terminate while the
   loop edited its own artifact.
3. **`band`** is priority under this repo's ranking directive. 1 blocks other
   work or risks data that cannot be recaptured, 2 is the reader chain
   everything waits behind, 3 is a sentence wrong where a reader acts on it,
   and 5 is deferred on purpose. No band 4 is defined, so no label exists for
   it.

`question` is not `decision`. An issue can carry `question` while it waits on
research rather than on the owner, as
[issue 273](https://github.com/l3a0/quantitative-trading/issues/273) did, so
the board reads only `decision` as needing the owner rather than a session.

### When two labels disagree

An issue carrying two `band:N` labels, both `working:` labels, two kinds, or
two different `Board order:` lines has no single value. The script takes the
lowest band, the `build` kind, the kind the table above puts first and the
first line, and lists each conflict in
the run's job summary rather than failing, because one stray label would
otherwise freeze the whole board. Read the summary of a run after setting
either, and fix the label the conflict names.

## What the page is made of

A header strip and three sections, top to bottom. The strip renders the two
`STATE` figures: the open issue count, and the stamp drawn from `updatedAt`.

It used to carry five more, and the owner removed all five on 2026-10-05 UTC.

1. The commit `main` stood at.
2. The vintage files and their rows.
3. The committed highlights.
4. The suite's test count.
5. The experiments tracked.

The test count alone cost a full suite run per update, 532 seconds on
`ec44e94`, and a merge during that run made the count describe a commit that
was no longer `main`, so the run had to start over. That happened the day they
were removed, when
[pull request 363](https://github.com/l3a0/quantitative-trading/pull/363)
merged mid-run. None of the five said what to take next, which is the question
this page answers, so do not add them back.

The sections are these.

1. **In flight**, five columns running most finished on the left: waiting on
   your review, waiting on my review, building, planned with no builder, and
   being planned. A card here is drawn once and left out of the build order.
   Two of the five hold a card only because a session is on it, and the kind
   of `working:` label is what separates a build session from a decompose
   loop. A third, waiting on my review, also holds a card whose branch is open
   and whose session has not handed it over.
2. **Build order**, four columns by dependency depth. By default they hold the
   ranked cards, and with Show all they hold everything not in flight.
   Within a column, cards sort by readiness, then by the priority order, then by
   a measured `after`, then by number, except that a card whose `kind` is
   `deferred` is forced last whatever the rest says. Under it sits a chainbar,
   which holds a hint until a card is picked and then says what that card waits
   on and what waits on it.

   By default the section draws only the cards `NEXT` ranks, and a line above
   the columns counts the rest and carries a **Show all** button. With every
   open issue drawn, the first column ran past fifty cards and the ten ranked
   ones were scattered through it. The Marketlake Build Board made the same cut
   at a hundred and fifty. The choice is kept in the viewer's browser under
   `qt-board-all` and nowhere else. A card whose `kind` is `deferred` stays
   hidden even when it carries a band, because `rankMark` drops it. A band of 5
   does not hide a card on its own. So a card in the build-order columns shows
   by default exactly when it carries a `band:N` label and its `kind` is not
   `deferred`. A card in flight shows either way. A band label is how a card
   gets onto the short view, and that view is what the owner reads first.
3. **One paragraph**, saying how the board is built and that every figure on
   it dates from the stamp. It is all that remains of a twenty-paragraph footer
   that was a second telling of what the cards say. Do not grow it back.

Between the strip and the first section sits a banner. Over a current board it
is empty. It warns when the stamp is older than `staleAfterMinutes`, because a
failed run leaves the last board up and a board an hour stale looks like a
fresh one. It also speaks when the page has no board to show, or has stopped
taking fresh copies, and says which and how old any data on screen is. With no
board data the page hides both sections and the footer and draws only the
banner, so a missing or unreadable `board.json` never reads as an empty board.

## Change the page's code

Change it only when the rendering has to change. Edit `board.html` beside this
skill, run `tests/test_build_board.py` and `tests/test_build_board_generator.py`
and the harness below, and open the pull request. The run of the Action that
the merge starts publishes `main`'s `board.html`, so there is nothing to
publish by hand.

A change to what the page reads is a change to the script as well. Add the
field to `scripts/build_board.py`, and to `ITEM_OK` in the page if the renderer
reads it without a guard, because the page refuses a whole section when one
item lacks a field it reads.

## Verify by executing, never by reading

A parse check is not enough, because a comma dropped inside a nested array still
parses. `tests/test_build_board.py` runs the page against an invented fixture,
which catches a page that throws, draws a section from the wrong document, or
mislabels an empty board. It cannot read the live data, so running the page on
a board built from GitHub is still the check on what a viewer will see.

The harness runs the page's script under `osascript`, which has no fetch, so it
hands the page a fake one serving a `board.json` built as "Where the board
lives" says. Run this from the scratch directory that build wrote into, with
`$REPO` set to this checkout.

```bash
python3 -c "
import json,re,sys
t=open(sys.argv[1]).read()
open('board.js','w').write(re.search(r'<script>(.*?)</script>', t, re.S).group(1))
open('serve.js','w').write('var fetch=function(){return Promise.resolve({ok:true,status:200,'
  'text:function(){return Promise.resolve('+json.dumps(open('board.json').read())+');}});};\n')
" "$REPO"/.claude/skills/update-build-board/board.html
cat > print.js <<'JS'
(async function(){ for (var i=0;i<50;i++) { await null; }
function s(x){return String(x).replace(/<[^>]+>/g," ").replace(/\s+/g," ").trim();}
var o=[];
o.push("STRIP: "+s(store.strip.innerHTML));
store.flow.innerHTML.split('<div class="col f-').slice(1).forEach(function(c){
  var h=c.match(/<span class="t">([^<]+)<\/span><span class="c">(\d+)<\/span>/);
  var ids=(c.match(/data-n="(\d+)"/g)||[]).map(function(m){return "#"+m.match(/\d+/)[0];});
  var d=c.match(/<span class="d">([^<]*)<\/span>/);
  o.push("flow  "+h[1]+"="+h[2]+": "+(ids.join(" ")||"(empty)"));
  o.push("  sub "+(d?d[1]:"(none)"));
  var wk=(c.match(/<div class="wk">[^<]*<\/div>/g)||[]).map(s);
  o.push("  wk  "+(wk.join(" | ")||"(none)"));});
store.board.innerHTML.split('<div class="col k').slice(1).forEach(function(c){
  var h=c.match(/<span class="t">([^<]+)<\/span><span class="c">(\d+)<\/span>/);
  var ids=(c.match(/data-n="(\d+)"/g)||[]).map(function(m){return "#"+m.match(/\d+/)[0];});
  var d=c.match(/<span class="d">([^<]*)<\/span>/);
  o.push("board "+h[1]+"="+h[2]+": "+ids.join(" "));
  o.push("  sub "+(d?d[1]:"(none)"));
  var wk=(c.match(/<div class="wk">[^<]*<\/div>/g)||[]).map(s);
  o.push("  wk  "+(wk.join(" | ")||"(none)"));});
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
console.log(o.join("\n")); })();
JS
cat "$REPO"/.claude/skills/update-build-board/dom-stub.js serve.js board.js print.js > run.js
osascript -l JavaScript run.js
```

The page fetches on load and draws once the answer arrives, which is after the
script's last line, so the printing waits for it rather than running at once.

That run draws the default view, which hides every card `NEXT` does not rank.
Run it a second time with the Show all view, because most of the columns and
most of the board note only render there. The stub has no `localStorage`, so
one line before the script supplies a stored choice. It answers only for the
page's own key, so a page reading a renamed key draws the short view and the
run shows it.

```bash
(cat "$REPO"/.claude/skills/update-build-board/dom-stub.js serve.js
 echo 'var localStorage={getItem:function(k){return k==="qt-board-all"?"1":null;},setItem:function(){}};'
 cat board.js print.js) > run-all.js
osascript -l JavaScript run-all.js
```

`osascript -l JavaScript` is JavaScriptCore, and it is what runs this where no
`node` is installed. It is macOS only. Anywhere else, run the same files with
whatever JavaScript engine is present, because the stub is plain ES5 and
assumes nothing about its host.

Print every surface the page renders into, not the interesting ones. An earlier
version of this harness skipped `foot`, `key` and `flowkey`, and `foot` is the
largest prose block on the page and the one holding the most hand-written
numbers. Planting a false figure in it left the output byte-identical, so the
check could not see the surface it was most needed on.

The column subtitles were the same gap a second time. The harness printed each
column's title and count and skipped the subtitle under them, so a change
rewriting the "Waiting on" subtitles for defect 17 could have been reverted
without the output moving. Each column now prints a `sub` line under it.

The session line was the third. On 2026-10-05 the page stopped drawing a
card's `what` phrase under "Building" and "Being planned", and the harness
printed the same output for that page and for one with the change reverted,
because it printed no card's lines at all. Each column now prints a `wk` line
listing the session phrases its cards drew, and `(none)` where they drew none.
Later the same day the page stopped drawing the phrase under "Waiting on my
review" as well, so every `wk` line now reads `(none)`, and a phrase showing up
on any of them is the line coming back.

**Much of the page is dark when no branch is open and no session holds a
card**, which is the state it is in between batches. The flow note collapses
to a sentence, the flow legend loses two entries, and the footer's decay clause
disappears entirely. That clause is where check 5's conjunction lives, so on an
empty board the sentence it warns about cannot be read at all. Where a change
touches that code, add a `prs` or `working` entry to a scratch copy of
`board.json`, rebuild `serve.js` from it, run the harness and read the output.

**Read the output rather than checking that it ran.** About half the defects
this page has shipped were sentences that rendered perfectly and said something
false. Six checks catch most of them.

1. **The totals reconcile.** In-flight cards plus board cards plus the hidden
   count on the `OTHER[more]` line equals open issues, and every card carries
   its labels. In the Show all run nothing is hidden, so the number on that
   run's `OTHER[more]` line must equal the board cards, and in-flight plus board
   cards alone must equal open issues.
2. **No sentence contradicts another.** The free-card list must not name a card
   that a later sentence says nobody should start.
3. **Every count matches its own list.** A sentence saying four cards and then
   naming three is the prose and the data disagreeing.
4. **No figure is typed into a sentence.** Every number the page renders should
   come from the data, so that changing the data changes the page. This
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
   ranking sorted by a measured argument, so the page put [issue 2](https://github.com/l3a0/quantitative-trading/issues/2) ahead of
   [issue 41](https://github.com/l3a0/quantitative-trading/issues/41) in one place and behind it in another. There is now one `cardOrder`
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
The rows from here on, apart from 13 and 14, were each caught by the owner
reading the published page rather than by a check. That is what they have in
common. Most had been on the page for a while, and two were made and found
inside one session, kept anyway because what produced each was two rules
meeting rather than one careless edit. They are the failures this page invites
and the ones a harness cannot see.

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
    sitting fourth in a column of twenty-five. Together they gave [issue 10](https://github.com/l3a0/quantitative-trading/issues/10) a
    chip reading 6 above a position reading last, which is two answers to one
    question. The chip is dropped on a deferred card, because the ranking holds
    one only to record that it is deliberately not being done, and the dashed
    border and the kind word already say that. The shape is not rare: the card
    renderer carries two other comments reasoning about giving one card two
    answers to one question. Check 6 above is what catches the next one, so a
    rule added to a card is read against the card's own position rather than
    only against the data it came from.
Defects 13 and 14 are a third kind. Both were made and caught inside one session
rather than by the owner reading the page. Defect 14 came from the harness
output. Defect 13 could not, for the reason it records, and came from reading
the script beside it. Each row after them says how it was found.

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

15. **A column test reading half of what its heading claims.** Caught by the
    owner reading the page. "Waiting on your review" asked only whether a review
    had been posted, so a branch with two
    checks still running sat under a heading saying the next move was the
    owner's. `CLAUDE.md` is explicit that a pull request is not handed over until
    its checks have settled, so the heading was making a promise the test did not
    check, and the page invited a merge of a branch that could still go red.

    The first attempt was worse than the defect. It kept the card in the owner's
    column and added a clause to the note saying its checks had not settled,
    which is the note working around a wrong test rather than the test being
    fixed, and it put the rule in a second place. That is defect 5 again. One
    `handedOver` came to decide it, the card stayed on the reviewer's side until
    both halves were done, and the note went back to one sentence. Defect 17
    later added a third condition.

    Three states stay on the reviewer's side and the third is the one to
    remember: a check still running, a check that failed, and no checks reported
    at all. A conflicting pull request gets no run created, so an empty rollup is
    a branch nothing built rather than a branch with nothing wrong.
16. **A heading that named one kind of session for two.** Found while publishing
    the fix above, which is the only reason it was not shipped. Adding decompose
    loops to `WORKING` put five cards under a column reading "Building", which is
    what a loop is not. A loop ends in a sharper plan and a builder ends in a branch,
    so they are different states and now have different columns. `kind` was
    already the field that told them apart, and the column test reads it.
17. **A column test that could not see the session still working.** Caught by
    the owner, after a session had recommended a merge from the column. On
    2026-10-05
    [issue 340](https://github.com/l3a0/quantitative-trading/issues/340) sat
    under "Waiting on your review". Its
    [pull request 383](https://github.com/l3a0/quantitative-trading/pull/383)
    had a review comment posted at 05:02Z and six green checks at `81b4e28`, so
    both halves defect 15 asks for were done. Its session was not. At 05:15Z it
    pushed a merge of `main`, moving the head to `125b5a6`, and it was then
    rewriting the post, the README and Entry 21. `handedOver` read the review
    and the checks and nothing about the session. The page's own comment said
    an entry owes its removal when its pull request opens, so the card carried
    no `WORKING` entry and no signal was left to read.

    This is defect 15 on the other half of the same heading. That one read a
    review and not the checks, and this one read both and not the session. The
    fix reuses `WORKING` rather than adding a field. A build session's entry
    now stays until it hands the pull request over, and comes out at the
    hand-over. Since
    [issue 533](https://github.com/l3a0/quantitative-trading/issues/533) the
    entry is a `working:build` label. The page's `owed` returns the first
    thing a branch still owes, which is a review, its session or its
    checks. The column test and the flow note both call it, so the reason a
    card gives for sitting on the reviewer's side is the rule that put it
    there, which is defect 5's lesson.

    The price is a card left under "Waiting on my review" when its session
    ends without taking its entry out. That fails safe, because it delays a
    merge rather than inviting one too early.
18. **A merged pull request read as a branch.** Found on 2026-10-10 by reading
    the Show all view.
    [Issue 431](https://github.com/l3a0/quantitative-trading/issues/431) and
    [issue 432](https://github.com/l3a0/quantitative-trading/issues/432) each
    had a pull request merged as `Part of`, with the issue left open for a link
    and a reference. The board note left both out of the free list and gave
    as its reason that a card can "already be written and waiting on a review",
    which neither was. The note asked whether `PRS` held any entry for the
    card, while the In flight section asked whether it held an open one, so
    the two sections disagreed about one card. That is defect 5 again. The same
    bare test also hid the plan marker, the kind word and the accent border on
    such a card, and put "a pull request carries it" in the legend. One
    function, `openBranches`, now answers the question for every reader.

    Freeing every merged entry would have gone past the defect. A pull request
    merged with no `Part of` was meant to close its issue, so the owner ruled
    on 2026-10-10 that its card is held back as needing only closing by hand,
    and `closesByHand` decides that for the free list, the plan marker, the
    kind word, the "Planned, no builder" column and the chain bar. The same
    reading found a closed entry's line repeating its old review text and,
    with no closing link, saying what merging would do. It now says closed.
19. **One sentence carrying two facts.** Caught by the owner reading the
    published page. On 2026-10-11
    [issue 303](https://github.com/l3a0/quantitative-trading/issues/303)
    gained `needs` of 249 and 510, both open and neither waiting on anything.
    The board note's branch for a graph with no third column was fixed text
    saying nothing sat "behind more than one thing", which meant no chain ran
    two steps and read as no card waiting on two issues. The second column's
    subtitle, "one thing has to land first", made the same claim about the card
    under it. That is defect 1 surviving inside a computed sentence, because
    only its other branch read the data. The deep branch had its own version,
    calling two steps "the deepest the graph goes" without measuring it.

    The note now reads the longest chain from the depth map, names any card
    waiting on several open issues in a clause of its own, and says nothing
    about depth when no card waits on anything. The columns are headed by steps
    along a chain rather than by things to land, and the note counts in the
    same steps. The review of that fix found the class in two more places. The
    shallow branch never said when it was counting cards the short view hid,
    which the deep branch already did. The chain bar said "waits on 2" for a
    card whose own line named one issue, because it counted the whole chain.
    So when a phrase can be read as either of two quantities, check it against
    data where the two differ.
20. **A free claim that read only the links.** Caught by the completeness lens
    of the review of
    [pull request 518](https://github.com/l3a0/quantitative-trading/pull/518),
    and filed as
    [issue 521](https://github.com/l3a0/quantitative-trading/issues/521).
    Picking a card with no open `needs` either way gave fixed text saying it
    could be taken on its own. That read only `needs`. So the bar called a
    card free whose kind word said not to start it, or whose session or open
    branch said somebody was carrying it. The board note's free list held
    those cards back, so the bar and the note answered one question in two
    places. That is defect 5 again. A card whose `after` line tied it to
    another issue was also called linked to nothing.

    One table, `HOLDS`, now lists the reasons a card is not free, and
    `takeable` passes ordinary work that no row of it holds. The free list and
    the bar both read them. The bar names the reasons a card is held, says
    only what the links show for a card blocked on data, and names an `after`
    tie in either direction. The review of that fix found two more places the
    bar disagreed with the card. A kind reason ignored the open branch that
    hides the card's kind word, so `kindShown` now decides both. A plan whose
    one open question is the owner's was called free while the In flight note
    said it waited on the owner. A row for it now reads `planMarker`, so it
    fires only where the card draws that marker.

    The completeness lens of that review found a third place, filed as
    [issue 573](https://github.com/l3a0/quantitative-trading/issues/573). The
    In flight note's sentence for "Planned, no builder" asked only whether a
    plan waited on the owner. So a deferred, decision, parent or data card with
    a finished plan was "planned and free for anyone to pick up" there while
    the bar said it was not free to take. That sentence now reads `takeable`
    and gives the reasons `HOLDS` names, in the bar's words. No row names data,
    so a card blocked on data is told only that it is not free, as the bar
    tells it only what its links show. The column's own test
    still reads no kind, so such a card stays under that heading, and the note
    beside it is what says the card is held.
21. **Two pointers reading a list that ties at zero.** Found by the over-reach
    lens of the review of
    [pull request 518](https://github.com/l3a0/quantitative-trading/pull/518),
    and `main`'s page before that pull request did the same.
    [Issue 523](https://github.com/l3a0/quantitative-trading/issues/523)
    recorded it. `most` is the largest number of cards any one card frees, and
    `unblocks` held every card that freed that many. When nothing waits on
    anything, `most` is 0 and every card ties at it, so the list held the whole
    board. The freeing clause read `most` and said nothing was freed by landing
    anything. The two pointers after it, `flownTop` and `hiddenNamed`, took
    their cards from the list. So the note named every card in flight, and in
    the short view every hidden card, as though each one freed the most.

    That is defect 1's lesson in a list of maxima. Such a list is never empty
    while the board holds a card, so the branch to compute is the one where it
    ties at zero. `unblocks` is now empty when `most` is 0. The cards waiting
    on several open issues still feed the hidden pointer, so the guard sits on
    the list rather than on the whole pointer.

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
rather than hidden, because nothing checks the two against each other.

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

Report in the same reply that sets anything.

1. Each label, link and line set or removed, and on which issue.
2. Any conflict the next run's job summary listed, and what fixed it.
3. Any sentence the harness caught, and what replaced it, when the page's code
   changed.

A run of the Action that fails leaves the last board up, and the page's banner
says so once the stamp passes `staleAfterMinutes`. Read the failed run's log
rather than re-running it, because a second run of the same read fails the same
way unless the failure was GitHub's.

### Offering a task per idle card was tried and withdrawn

For part of 2026-09-18 this skill told a session to offer a build task for every
card left in "Planned, no builder" and a decompose task for every card in the
Build order's first column that nothing blocked, that no session or branch
carried, and that was neither deferred nor waiting on an owner decision. The
owner withdrew both the same day. It is written down so the next session reading
an idle column does not re-invent it.

Two things went wrong, and neither depends on how large the queue is, which
matters because nobody has established that.

1. **The offer is larger than the queue.** That column held 27 such cards on
   2026-09-18, so one update offered 28 tasks, one per card plus a build task for
   the single planned card. The owner started six while the offers were still
   being made, which took those six out of the queue, and two of the rest were
   dropped to make room.
2. **A drop is not always reported.** The tool named one of the two. The other
   was visible only by diffing the pending list across two calls, and a diff
   cannot tell an eviction from a task somebody started, so the identity of the
   second is inferred rather than read.

The second is the reason to withdraw rather than to shrink the batch, and it is
a judgement rather than a measurement, because nothing here priced what a silent
drop costs a reader. The argument is that a queue looks like a list, so a reader
who takes it for one is misled by exactly the entries nobody is told about, and
that does not improve at five cards.

**Do not write a capacity into this file**, because
[issue 117](https://github.com/l3a0/quantitative-trading/issues/117) is open
against the sentence that did. A tool result named twenty while a session
measured a first eviction at six pending, and the same session then watched
chips leave with no offer and no dismissal to explain it, so neither number is
settled and the pending list may be a window rather than the queue. That issue
says how to measure it. Until somebody does, the account above is written so it
holds at any size.

Which card is dropped is worth stating carefully, because the first draft of
this record got it wrong. The queue drops the oldest still pending, which is the
front of whatever the owner has not started, not the front of the priority
order. Offering in priority order and starting from the top leaves the
highest-ranked card the owner declined as the one at risk.

So an update reports what it found in those two states and stops. What to start,
and how many at once, is the owner's call. Their ceiling is eight running at
once, set the same day and not withdrawn, and what argued for a ceiling was
measured: three concurrent sessions produced two publish refusals inside one
board update, and each refusal cost a full read of the live page and a merge
decided part by part. Moving the data into the database on 2026-10-02 removed
that cost for data updates, so the ceiling now rests on the owner's attention
rather than on refusals. Nothing in this skill starts anything, so the number is
recorded here rather than enforced.

One fact from the withdrawn text is about the page rather than about offering,
so it stays, corrected. The "Planned, no builder" test in `FLOW` asks five
things of the state `flightCols` builds for a card.

1. `s.plan`: a `PLANNED` entry exists.
2. `!s.pr`: no open pull request carries the card.
3. `!s.busy`: no session is on it.
4. `!s.blocked`: nothing in its `needs` is still open.
5. `!s.landed`: no pull request merged against it with no `Part of`.

The withdrawn text said the test never read `needs`, so a plan-complete card
behind an open blocker would land in that column too.
[Issue 138](https://github.com/l3a0/quantitative-trading/issues/138) was the
first card to reach that state, and the fourth condition was added for it, so
such a card stays on the depth board under its own "waits on" line. The fifth
came with the owner's ruling of 2026-10-10, under defect 18, because a card
whose pull request merged with no `Part of` has no builder to wait for.
