---
name: sync-substack
description: Create a Substack draft from a blog/*.md post, or bring an existing draft or published post back in line with its Markdown. Use when asked to create or publish a post on Substack, to push a post's Markdown edits to its draft, to pull the owner's Substack editor edits back into the Markdown, or to check that a draft and its Markdown still say the same thing.
---

# Sync a blog post with Substack

Each post in `blog/` exists twice. The Markdown is the copy the repository
reviews and tests, and the Substack draft is the copy readers see. The owner
also edits drafts directly in Substack's editor. So the two copies drift unless
every change lands in both, in both directions, and a write to Substack never
destroys an edit the owner made there.

The work runs inside the owner's signed-in Substack page, because the API it
calls needs that page's session. That is why the converter exists twice beside
this file.

1. `md2substack.py` converts a post locally and prints the hashes a write is
   checked against.
2. `md2substack.js` is the same converter for the page. The page fetches the
   Markdown from GitHub at a pinned commit, converts it, and refuses to write
   unless the result hashes to the local conversion.

`tests/test_substack_converter.py` pins the converter's output on the fixtures
under `tests/fixtures/substack/`, converts every committed post, and checks
that the two files agree. The Python
file's docstring lists what each Markdown shape becomes.

## This file and the owner's notes

The owner keeps private notes outside this repository with a record per post.
Each record holds the draft's id, the commit it was last synced to, the hashes
it read back with, and any choice the owner made for that post, such as
leaving its subtitle blank. Those records stay private, because this repository
is public.

This file is the authority for procedure. When it and the notes disagree on how
to do something, this file wins and the notes get corrected. When they
disagree on a fact about one post, the notes win, since this file holds none.

Nothing account-specific goes into this repository. That covers draft ids,
byline ids, cookies, tokens, session ids and the URLs of uploaded images.

## Before any write

1. **Know which writes need the owner.** Creating an unpublished draft and
   syncing one need no ask, by the owner's standing approval of 2026-10-10,
   which `CLAUDE.md`'s `## Write-ups and their Substack drafts` records.
   Publishing, scheduling and sending stay the owner's call, and so does any
   write to a post that is already published, as the last section explains.
   A draft the owner has scheduled counts as published, because a write to it
   changes what goes out.
   The standing approval covers the write and not the comparison before it.
   Every sync still compares the live draft with its recorded baseline first,
   and an edit the owner made in the editor goes into the Markdown rather
   than being overwritten.
2. **Look for an existing draft.** Read the owner's notes, then list the
   drafts. Sessions have twice been sent to create a draft that already
   existed, and only this lookup stopped a duplicate.
   `GET /api/v1/post_management/drafts?offset=0&limit=50&order_by=draft_updated_at&order_direction=desc`
   lists unpublished drafts. `GET /api/v1/drafts` looks like the same list but
   returned only published posts, so it misses every draft. Check
   `/api/v1/post_management/scheduled` and `/api/v1/post_management/published`
   too. The published list refused a request with no `order_by`, and
   `order_by=post_date&order_direction=desc` worked.
3. **Pin the commit.** The page reads the Markdown and the figures from
   `raw.githubusercontent.com` at a commit, so that commit must be pushed. Run
   `git log` on the post right before writing, not only at the start, because
   a pull request that merges meanwhile changes what the draft should hold.

## Check the post before converting it

1. **The subtitle fits in 255 characters.** Substack refuses a longer
   `draft_subtitle` with "Subtitle is too long", and 255 passed where 256
   failed. `--summary` prints `subtitle_length`. A longer subtitle is the
   owner's call. The choices so far have been to shorten the Markdown, or to
   create the draft with a blank subtitle and keep the Markdown as approved.
   Never cut it on Substack alone, since that makes the two copies differ.
2. **The subtitle holds no Markdown beyond escapes.** The converter drops the
   backslash from `\$` and `\~` in the subtitle through the same function the
   body uses. Anything else there, such as a link or emphasis inside the
   line, reaches Substack as typed. Remove it from the value sent, and say so
   in the report.
3. **Every equation renders as Substack draws it.** Substack renders LaTeX with
   MathJax 3, recognisable by its `mjx-` elements, with the TeX packages `base`,
   `ams`, `newcommand`, `noundefined`, `require`, `autoload` and
   `configmacros`. It has no `textmacros`, so inside `\text{}` and `\texttt{}`
   every character prints as typed. A `\%` there prints its backslash, so write
   `8.7\%` in math mode rather than inside `\text{}`. A `\_` there prints its
   backslash too, so write `\texttt{VX}\_\texttt{ES.m}` rather than
   `\texttt{VX\_ES.m}`. Fix the Markdown first, then the draft. The converter
   writes a pipe table's cells by the same rule, with every special character
   outside `\text{}`, and its docstring states the rule.
4. **The post names no issue or pull request.** The owner's rule for blog
   posts is to say what an issue held rather than cite it.
5. **The post uses only shapes the converter handles.** The Python file's
   docstring lists them. A pipe table becomes a LaTeX `array` in a math
   block, by the owner's ruling of 2026-10-10, and its cells lose their links
   and inline formatting. Read the converted table before sending it, since a
   cell that relied on a link loses it. A shape the docstring does not list,
   such as a block quote or a horizontal rule, comes out as a paragraph of
   literal Markdown. A new shape needs the converter to learn it first, in
   both languages and with the fixtures extended. The test suite fails when a
   committed post leaves a paragraph opening `|`, `#` or `![`.

To check an equation the way Substack draws it, open any published post page,
where `window.MathJax` exists, and run `MathJax.tex2mml(expr, {display: true})`.
Look for `merror` and for a backslash inside `mtext`. A KaTeX check does not
catch either failure, because KaTeX supports `\%` inside `\text{}` and MathJax
without `textmacros` does not.

## Work from the drafts list page

Run every script from the drafts list page, never from the editor. The editor
autosaves, and an editor tab open on an older version has saved it back over
five later writes made through the API. If the owner has an editor tab open on
the post, ask them to leave it before writing and to reload it afterwards.

Three limits of the browser decide how the scripts are built.

1. **The output filter.** The Claude in Chrome extension blocks raw draft text
   in its output and hides strings that look like hashes. So compare inside
   the page and return booleans and counts, such as `{convOk: true, blocks: 70}`.
2. **No local server.** An https page cannot fetch from `http://127.0.0.1`, and
   a POST to a local receiver hung on Chrome's local-network prompt and froze
   the tab. So the page reads from `raw.githubusercontent.com` instead.
3. **No large inline payloads.** Typing a converted tree of 30 to 40 KB into a
   script went wrong. Converting in the page with `md2substack.js` is the
   route that worked. Sending the tree gzipped and base64-encoded, unpacked in
   the page with `DecompressionStream` and checked by hash, also worked.

When the extension cannot script the page, stop and tell the owner. Do not
route around the extension to reach the signed-in page another way.

## Create a draft

1. **Upload each figure.** In the page, fetch the PNG from
   `raw.githubusercontent.com` at the pinned commit and send it to
   `POST /api/v1/image` with body `{image: dataUrl}`. Check that the served
   image's bytes hash to the committed PNG's. Write `images.json`, which maps
   each file name to the `url` the upload returned and the PNG's `width`,
   `height` and `bytes`.
2. **Convert locally.** Run the converter with `--summary` and keep the hashes
   it prints. `md_sha256` hashes the file's bytes, which is what the page
   hashes after fetching it, so it goes into the driver's `EXPECT.md`.

   ```bash
   python3 .claude/skills/sync-substack/md2substack.py --summary blog/<post>.md images.json
   ```

3. **Dry-run in the page.** Send `md2substack.js` followed by a driver like the
   one below. It checks the Markdown's hash before converting it, so a wrong
   file is never converted. It refuses to write unless the Markdown and its
   conversion both hash to what the local run printed, unless a flag set by a
   separate call says to go, and unless the drafts, scheduled and published
   lists all load and none holds the title. The first call only reports, so a
   mistake costs nothing. The driver reads the flag and clears it on its first
   line, so a script that throws partway cannot leave it set for the next one.
4. **Create.** Set `window.__GO = "create"` in its own call, then send the same
   script again. Leave `draft_bylines` empty. The owner sets the byline in the
   editor.
5. **Read it back.** `GET /api/v1/drafts/<id>` returns `draft_body` as a JSON
   string. Parse it, then check that `M2S.canon` of it hashes to the local
   `body_sha256` and that `M2S.walkLines(body).join("\n")` hashes to the local
   `walk_sha256`. Check the block count and where the widgets sit too.
6. **Record it.** The draft's id, the commit and the hashes go into the
   owner's notes. They are the baseline the next sync compares against.

A draft created this way gets the publication's default audience, which the
owner sets at publish.

```javascript
// md2substack.js goes above this line, unchanged.
const GO = window.__GO;
window.__GO = null;
const COMMIT = "<full commit sha>";
const POST = "blog/<post>.md";
const EXPECT = { md: "<md_sha256>", conversion: "<conversion_sha256>" };
const IMAGES = { /* the contents of images.json */ };
const LISTS = [
  "/api/v1/post_management/drafts?offset=0&limit=50&order_by=draft_updated_at&order_direction=desc",
  "/api/v1/post_management/scheduled",
  "/api/v1/post_management/published?offset=0&limit=50&order_by=post_date&order_direction=desc",
];
const sha = async (s) => Array.from(new Uint8Array(await crypto.subtle.digest(
  "SHA-256", new TextEncoder().encode(s)))).map((b) => b.toString(16).padStart(2, "0")).join("");
// The posts in one list, or null unless the request succeeded and returned an array.
const posts = async (path) => {
  const r = await fetch(path);
  const list = r.ok ? await r.json() : null;
  return list && Array.isArray(list.posts) ? list.posts : null;
};
const md = await (await fetch(
  `https://raw.githubusercontent.com/l3a0/quantitative-trading/${COMMIT}/${POST}`)).text();
const out = { mdOk: (await sha(md)) === EXPECT.md };
if (out.mdOk) {
  const draft = M2S.convert(md, IMAGES);
  out.convOk = (await sha(M2S.canon(draft))) === EXPECT.conversion;
  out.subtitleLength = draft.subtitle.length;
  out.blocks = draft.body.content.length;
  if (out.convOk && GO === "create") {
    const lists = await Promise.all(LISTS.map(posts));
    if (lists.some((list) => list === null)) {
      out.refused = "a post list did not load as an array";
    } else if (lists.flat().some((p) => p.draft_title === draft.title || p.title === draft.title)) {
      out.refused = "a post with this title exists";
    } else {
      const r = await fetch("/api/v1/drafts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_title: draft.title,
          draft_subtitle: "<the subtitle as checked above, or an empty string>",
          draft_body: JSON.stringify(draft.body),
          draft_bylines: [],
          type: "newsletter",
        }),
      });
      out.created = { status: r.status, ok: r.ok };
    }
  }
}
out;
```

The owner's notes do not record the fields these lists return. The drafts check
this file carried first read an array under `posts`, each entry with a
`draft_title`. So the driver reads `posts` from all three lists and matches the
title against both `draft_title` and `title`. When it refuses because a list
did not load as an array, read that list's response and correct the driver
here rather than dropping the check.

## Sync an existing draft

A sync converts the post with the figures the draft already holds, so nothing
is uploaded again. Build `images.json` from the live draft's `image2` nodes.
Key each entry by the figure's file name, the last part of the path in the
Markdown's image line. Take `url` from the node's `src`, and `width`, `height`
and `bytes` from the attributes of the same names. The local conversion then
reproduces the draft's image nodes.

1. **Read the live draft and compare it with its baseline.** Walk its body
   with `M2S.walkLines` and hash the lines in the page. A walk hash equal to
   the baseline in the owner's notes means the draft carries no text edits
   since the last sync. It says nothing about formatting, because the walk
   leaves out three things.
   1. A heading's level.
   2. A mark's attributes, such as a `textStyle` colour or a highlight colour.
   3. A block's `textAlign`.

   So also hash `M2S.canon` of the live body and compare it with the body
   hash the notes recorded at the last sync. Where the notes record none,
   compare the live body with the conversion of the last synced commit node by
   node, attributes included. The sync goes ahead only when both comparisons
   match. A body that differs while the walk matches carries a formatting
   change, or an attribute the editor added on a save, and step 3 finds out
   which.
2. **Compare the title and subtitle too.** Check `draft_title` and
   `draft_subtitle` against the conversion's `title` and `subtitle`. Respect
   any choice the notes record for the post, such as a subtitle left blank
   or worded differently on purpose. A change the owner made to either in
   the editor goes into the Markdown like any other owner edit, under step 4.
3. **When it differs, find out why before writing anything.** The version
   history is readable. `GET /api/v1/drafts/<id>/versions` lists the saves, and
   `POST /api/v1/drafts/<id>/load_version` with body
   `{"version_key": "<key>"}` returns one without restoring it. Compare the
   draft with the conversions of several earlier commits too. An editor tab
   left open on an old version saves that version back, and the difference
   then is a revert rather than an edit.
4. **Sort each difference into one of three kinds.**
   1. Text the owner changed goes into the Markdown first, through the usual
      pull request, and the draft is then written from that Markdown.
   2. A change the editor made on its own is restored in the sync's write,
      and the owner is told why.
      One editor save turned `4\%` into `4%` inside a LaTeX block, which breaks
      the block, and added a trailing space to a paragraph. Neither changes
      the visible text, so neither is an owner edit.
   3. A node the owner added that Markdown cannot express is kept by copying
      it into the new conversion at the same place. Subscribe widgets the
      owner inserted, highlight marks and coloured text are the cases so far.
5. **Patch the changed blocks in place.** Replace only the top-level blocks
   that differ, and never rebuild the whole body from Markdown, because a
   rebuild silently drops everything in the third kind above. A comparison
   that covered only top-level paragraphs and headings once let a rebuild
   overwrite the owner's edits inside list items. So compare every node that
   carries text, including list items, captions, LaTeX blocks, image alt text
   and marks.
6. **Guard the write.** Build the patched body in the page and check that it
   hashes to the local conversion with the owner's nodes spliced in, before
   sending it. Splicing by index has put a new list item on the wrong block,
   and only this whole-document hash caught it. Then send
   `PUT /api/v1/drafts/<id>` only if `draft_updated_at` and each replaced
   block still read as they did, so an edit made in between is refused rather
   than overwritten.
7. **Verify both directions.** Every text unit in the draft is in the
   Markdown, and every one in the Markdown is in the draft. Record the new
   walk hash and body hash in the owner's notes as the next baseline.

A run-level patch can split one text run into two neighbours with the same
marks. They read identically but walk as two lines. When a draft's walk differs
by only such a split, merge neighbouring runs that carry the same marks on both
sides before comparing, and say in the notes that this draft needs it.

## When the converter's output changes

A change to the converter that changes what it produces for a post changes
that post's `conversion_sha256`, `body_sha256` and `walk_sha256`. The hashes in
a draft's record were read back from the live draft, so the first comparison
in a sync still holds against them. What stops holding is the fallback, which
compares the live body with a fresh conversion of the last synced commit.

1. **Compare with the recorded hashes first.** They come from the live draft
   and do not depend on the converter.
2. **Convert old commits with the old converter.** Where the record holds no
   body hash, convert the last synced commit with the converter as it stood
   at that sync. `git log` on `md2substack.py` names the commits, and
   `git show <commit>:.claude/skills/sync-substack/md2substack.py` gives the
   file.
3. **Expect the new conversion to differ in the touched blocks only.** Those
   differences come from the converter rather than the owner, so the sync
   writes them from the new conversion, and the report names each one.
4. **Record a fresh baseline.** Once the write is verified, its hashes go into
   the owner's notes as the next baseline.

The converter learned pipe tables, headings of four to six hashes and linked
images on 2026-10-10, and the subtitle lost its escapes the same day. A draft
made from a post with a table, a deep heading, a linked image, or a `\$` or
`\~` in its subtitle gets a new conversion hash from that change. Every other
committed post converts to the hashes it had before, which the pull request
measured.

## Update a published post

Every write here waits for the owner's approval in chat. The standing approval
for unpublished drafts does not reach a published post, because both steps
below act on a post readers can already see. A scheduled draft falls under
this section too.

A published post takes two steps, and the first alone changes nothing a reader
sees.

1. `PUT /api/v1/drafts/<id>` changes the post's draft only. The public
   `GET /api/v1/posts/<slug>` keeps serving the old body.
2. The live post changes when the owner, or a session the owner approved for
   that post, clicks the editor's Update button and then "Update now" in the
   panel that opens. On 2026-10-03 that panel offered no email option, sent
   no email, and kept the original publish date.

The public API can serve the old body for a few seconds after an update, so
re-read it with a query string that defeats the cache before concluding the
update failed. Patch a published post in place, as for a draft. One published
post carries the owner's highlight marks and coloured status words, and a
rebuild would drop them.
