---
name: update-build-board
description: Update the Quantitative Trading Build Board artifact after work on this repo changes what it shows. Use when a session has opened or merged a pull request, filed or closed issues, or finished a decompose loop, and when asked to refresh or update the board. Needs the Artifact tool. Answering what to take next is a read and does not on its own call for a republish.
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

Every figure on the page has a command behind it. Run them. A count carried in
your head from earlier in the session is the one that will be wrong, and it has
been: an update shipped 39 open issues when a query said 40.

```bash
git fetch --prune origin && git log --oneline -1 origin/main
gh issue list --state open --limit 100 --json number --jq 'length'
gh pr list --state open --json number,title,mergeable,statusCheckRollup,closingIssuesReferences
uv run pytest -q --no-header 2>&1 | tail -1
python3 -c "import json;print(sum(json.loads(l)['row_count'] for l in open('data/vintages.jsonl')))"
grep -c 'Location' research/book-notes/quantitative-trading.md
```

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
to tell a plain keyword from one inside a code span. Read the checks against the
pull request's current head, because a rollup is a claim about one merge ref at
one moment and goes stale in both directions.

## The data blocks, and what each owns

Everything the page says comes from one object and six arrays in its script.
They are not adjacent: `STATE`, `PRS`, `WORKING`, `PLANNED` and `NEXT` sit
together near the top, `TRACKER` is about a third of the way down, and `FLOW` is
near the bottom beside the code that reads it. Find each by name rather than by
scrolling. Change the data. Never hand-write a sentence stating a number the
data already carries, because that sentence outlives the number.

| Block | Holds |
| --- | --- |
| `STATE` | `main`, `updatedAt`, `vintages`, `suite.tests`, `notes.highlights`, `issues.open`, `issues.tracked` |
| `PRS` | per pull request: `pr`, `issue`, `state`, `linked`, `reviewed`, `review`, `rollup` |
| `WORKING` | cards a session is on now, each with `kind` of `build` or `decompose` |
| `PLANNED` | cards whose decompose loop exited: `n`, `passes`, `ready`, `note` |
| `TRACKER` | every open issue as a card: `n`, `ms`, `needs`, optional `after`, `kind`, `label` |
| `NEXT` | the ranking, each keyed by `issue` rather than `n`, with `band`, `ready`, `title`, `why`, and an optional `order` |
| `FLOW` | the four in-flight stages and the test that assigns a card to one |

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
o.push("RANK: "+store.rank.innerHTML.split("<li>").slice(1)
  .map(function(i){return "#"+i.match(/#(\d+)<\/a>/)[1];}).join(" > "));
o.push("KEY: "+s(store.key.innerHTML));
o.push("FLOWKEY: "+s(store.flowkey.innerHTML));
store.foot.innerHTML.split("<p>").slice(1).forEach(function(x,i){
  o.push("FOOT["+(i+1)+"] "+s(x));});
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
false. Four checks catch most of them.

1. **The totals reconcile.** In-flight cards plus board cards equals open issues.
2. **No sentence contradicts another.** The free-card list must not name a card
   that a later sentence says nobody should start.
3. **Every count matches its own list.** A sentence saying four cards and then
   naming three is the prose and the data disagreeing.
4. **Every number in the footer is one you measured this session.** That block is
   hand-written prose rather than computed, so nothing else will catch it.

## What goes wrong, from the record

Each of these shipped or was caught at the last moment. They are written down
because the next one will be a variant rather than something new.

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
   comparator and both sections call it. Keep it that way.
6. **A key describing cards that moved.** Each section computes its legend from
   what it drew. A fixed legend advertises states that are not below it.
7. **Declaration order.** `planOf` was read by a sort that ran before its
   declaration, which throws on load rather than degrading quietly. The stub
   catches this immediately.
8. **Pluralisation.** `plu` appended a bare letter s, giving a count of passes
   that read "19 passs". It now handles a word already ending in one.

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

## Finishing

Publish, then report in the same reply.

1. The version number and what moved.
2. Any sentence the execution caught, and what replaced it.
3. What is still stale, including the two sibling pages.

If a publish is refused because the artifact moved, do not force it. Read the
live version, merge onto it, and publish again. Forcing discards somebody's work.
