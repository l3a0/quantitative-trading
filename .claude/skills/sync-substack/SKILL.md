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

`tests/test_substack_converter.py` pins the converter's output on a fixture,
converts every committed post, and checks that the two files agree. The Python
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

1. **Get the owner's approval in chat.** Creating a draft and changing one are
   both writes to the owner's publication. A write to a published post is
   public at once.
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
2. **The subtitle holds no Markdown.** The converter copies the italic line as
   typed, escapes included, while the body loses them. A `\$` there would show
   its backslash on Substack. Remove the escape from the value sent, and say so
   in the report.
3. **Every equation renders as Substack draws it.** Substack renders LaTeX with
   MathJax 3, recognisable by its `mjx-` elements, with the TeX packages `base`,
   `ams`, `newcommand`, `noundefined`, `require`, `autoload` and
   `configmacros`. It has no `textmacros`, so inside `\text{}` and `\texttt{}`
   every character prints as typed. A `\%` there prints its backslash, so write
   `8.7\%` in math mode rather than inside `\text{}`. A `\_` there prints its
   backslash too, so write `\texttt{VX}\_\texttt{ES.m}` rather than
   `\texttt{VX\_ES.m}`. Fix the Markdown first, then the draft.
4. **The post names no issue or pull request.** The owner's rule for blog
   posts is to say what an issue held rather than cite it.

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

Four limits of the browser decide how the scripts are built.

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
4. **A page the extension cannot script.** When that happened, an AppleScript
   JXA runner that called `tab.execute({javascript})` with a script read from
   a file did the same job.

## Create a draft

1. **Upload each figure.** In the page, fetch the PNG from
   `raw.githubusercontent.com` at the pinned commit and send it to
   `POST /api/v1/image` with body `{image: dataUrl}`. Check that the served
   image's bytes hash to the committed PNG's. Write `images.json`, which maps
   each file name to the `url` the upload returned and the PNG's `width`,
   `height` and `bytes`.
2. **Convert locally.** Run the converter with `--summary` and keep the hashes
   it prints.

   ```bash
   python3 .claude/skills/sync-substack/md2substack.py --summary blog/<post>.md images.json
   ```

3. **Dry-run in the page.** Send `md2substack.js` followed by a driver like the
   one below. It refuses to write unless the Markdown and its conversion both
   hash to what the local run printed, and unless a flag set by a separate call
   says to go. The first call only reports, so a mistake costs nothing.
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
const COMMIT = "<full commit sha>";
const POST = "blog/<post>.md";
const EXPECT = { md: "<sha256 of the Markdown file>", conversion: "<conversion_sha256>" };
const IMAGES = { /* the contents of images.json */ };
const sha = async (s) => Array.from(new Uint8Array(await crypto.subtle.digest(
  "SHA-256", new TextEncoder().encode(s)))).map((b) => b.toString(16).padStart(2, "0")).join("");
const md = await (await fetch(
  `https://raw.githubusercontent.com/l3a0/quantitative-trading/${COMMIT}/${POST}`)).text();
const draft = M2S.convert(md, IMAGES);
const out = {
  mdOk: (await sha(md)) === EXPECT.md,
  convOk: (await sha(M2S.canon(draft))) === EXPECT.conversion,
  subtitleLength: draft.subtitle.length,
  blocks: draft.body.content.length,
};
if (out.mdOk && out.convOk && window.__GO === "create") {
  const list = await (await fetch("/api/v1/post_management/drafts?offset=0&limit=50"
    + "&order_by=draft_updated_at&order_direction=desc")).json();
  if ((list.posts || []).some((p) => p.draft_title === draft.title)) {
    out.refused = "a draft with this title exists";
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
window.__GO = null;
out;
```

The output filter has let a created draft's id through, since it is a number rather than a hash.

## Sync an existing draft

1. **Read the live draft and compare it with its baseline.** Walk its body
   with `M2S.walkLines` and hash the lines in the page. When the hash equals
   the baseline in the owner's notes, the draft carries no edits since the
   last sync, and the sync can go ahead.
2. **When it differs, find out why before writing anything.** The version
   history is readable. `GET /api/v1/drafts/<id>/versions` lists the saves, and
   `POST /api/v1/drafts/<id>/load_version` with body
   `{"version_key": "<key>"}` returns one without restoring it. Compare the
   draft with the conversions of several earlier commits too. An editor tab
   left open on an old version saves that version back, and the difference
   then is a revert rather than an edit.
3. **Sort each difference into one of three kinds.**
   1. Text the owner changed goes into the Markdown first, through the usual
      pull request, and the draft is then written from that Markdown.
   2. A change the editor made on its own is restored, and the owner is told.
      One editor save turned `4\%` into `4%` inside a LaTeX block, which breaks
      the block, and added a trailing space to a paragraph. Neither changes
      the visible text, so neither is an owner edit.
   3. A node the owner added that Markdown cannot express is kept by copying
      it into the new conversion at the same place. Subscribe widgets the
      owner inserted, highlight marks and coloured text are the cases so far.
4. **Patch the changed blocks in place.** Replace only the top-level blocks
   that differ, and never rebuild the whole body from Markdown, because a
   rebuild silently drops everything in the third kind above. A comparison
   that covered only top-level paragraphs and headings once let a rebuild
   overwrite the owner's edits inside list items. So compare every node that
   carries text, including list items, captions, LaTeX blocks, image alt text
   and marks.
5. **Guard the write.** Build the patched body in the page and check that it
   hashes to the local conversion with the owner's nodes spliced in, before
   sending it. Splicing by index has put a new list item on the wrong block,
   and only this whole-document hash caught it. Then send
   `PUT /api/v1/drafts/<id>` only if `draft_updated_at` and each replaced
   block still read as they did, so an edit made in between is refused rather
   than overwritten.
6. **Verify both directions.** Every text unit in the draft is in the
   Markdown, and every one in the Markdown is in the draft. Record the new
   walk hash in the owner's notes as the next baseline.

A run-level patch can split one text run into two neighbours with the same
marks. They read identically but walk as two lines. When a draft's walk differs
by only such a split, merge neighbouring runs that carry the same marks on both
sides before comparing, and say in the notes that this draft needs it.

## Update a published post

A published post takes two steps, and the first alone changes nothing a reader
sees.

1. `PUT /api/v1/drafts/<id>` changes the post's draft only. The public
   `GET /api/v1/posts/<slug>` keeps serving the old body.
2. The live post changes when the owner, or a session with the owner's
   approval, clicks the editor's Update button and then "Update now" in the
   panel that opens. On 2026-10-03 that panel offered no email option, sent
   no email, and kept the original publish date.

The public API can serve the old body for a few seconds after an update, so
re-read it with a query string that defeats the cache before concluding the
update failed. Patch a published post in place, as for a draft. One published
post carries the owner's highlight marks and coloured status words, and a
rebuild would drop them.
