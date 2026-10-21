// The in-page sync of an existing Substack draft, for the page that already
// holds md2substack.js's M2S.
//
// Why this file exists. A session syncs a draft from a page on the
// publication, by defining a function there and calling it once per edit. The
// function lived only in the page, so a browser pane that closed took it with
// it, and the session pasted about 10 KB of script back in. Most of that was
// one post's map of uploaded images. That happened twice on 2026-10-20. With
// the function committed here, SKILL.md's restore fetches this file at a
// pinned commit, checks its sha256 and evaluates it, and nothing post-specific
// is pasted at all.
//
// Nothing account-specific is committed, which SKILL.md requires because this
// repository is public. The draft id is an argument. The image map is built
// in the page from the live draft, by pairing the figure names in the last
// synced commit's Markdown with the draft's image nodes in document order.
//
// Usage, after M2S is defined:
//
//   await SYNC.syncTo({
//     draft: "<draft id>", post: "blog/<post>.md",
//     base: "<commit last synced>", commit: "<commit to sync to>",
//     expect: { md, conversion, body, walk, liveBody },
//     images: { "<file name>": { url, width, height, bytes } },
//     write: true,
//   })
//
// Each expect value is a sha256, whole or its first 8 or more hex digits.
// md, conversion, body and walk are md2substack.py --summary's md_sha256,
// conversion_sha256, body_sha256 and walk_sha256 for the post at commit.
// liveBody, which may be left out, is the body hash the owner's notes
// recorded at the last sync. images, which may be left out, adds to the map
// built from the draft or replaces entries in it, for a figure new or
// re-uploaded since base. Without write: true the call only reports. The
// result holds booleans, counts, reasons and the first 12 hex digits of the
// body read back after a write, since the browser extension hides raw draft
// text and strings that look like hashes.
//
// What it refuses, each before any write.
//
// 1. A configuration it cannot use, or a read that fails.
// 2. A draft that is published or scheduled, since a write to one needs the
//    owner's approval in chat.
// 3. A Markdown file that does not hash as expected, or a live body that
//    does not hash to liveBody when that is given.
// 4. A base Markdown whose figures do not pair with the draft's images, a
//    figure at commit with no image in the map, or a conversion that throws.
// 5. A conversion that does not hash as expected.
// 6. A live body that differs from the conversion of the base commit in
//    anything but its subscribe widgets. The splice copies changed blocks
//    from the new conversion, so a node the owner added in the editor, such
//    as a highlight mark, would be lost. SKILL.md's manual steps handle that.
// 7. A change that would add or drop a widget, or a patched body or walk that
//    does not hash as expected.
// 8. A draft that moved between the first read and the write.
//
// It reports whether the title and the subtitle match the conversion's but
// does not refuse on either, since the write leaves both alone and many
// drafts keep a blank subtitle on purpose. A write that fails, or a read-back
// that does not match, comes back as failed rather than refused, with what is
// known so far.
//
// Widgets are equal to each other whatever their attributes, because the
// editor rewrites them. The patch keeps every live widget in its live order,
// including one inside the changed blocks, and hashes the body with the
// conversion's widgets in their place, so the hash is the local body_sha256.
// That hash checks the non-widget blocks. Where the live widgets go rests on
// splice itself, which tests/test_substack_sync.py pins.
var SYNC = (function () {
  var RAW = "https://raw.githubusercontent.com/l3a0/quantitative-trading/";
  var COMMIT = /^[0-9a-f]{40}$/;
  var HASH = /^[0-9a-f]{8,64}$/;
  var DRAFT = /^[0-9]+$/;
  var POST = /^blog\/[a-z0-9][a-z0-9-]*\.md$/;
  var EXPECTED = ["md", "conversion", "body", "walk"];

  function message(err) { return String((err && err.message) || err); }

  // A block Markdown cannot produce whose attributes the editor owns.
  function isWidget(n) {
    return !!n && n.type !== "paragraph" && /widget|subscribe|button|cta/i.test(n.type || "");
  }
  function same(a, b) {
    return (isWidget(a) && isWidget(b)) || M2S.canon(a) === M2S.canon(b);
  }
  // Two lists of blocks that are equal block by block, widgets as equal.
  function sameBlocks(a, b) {
    if (a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) if (!same(a[i], b[i])) return false;
    return true;
  }
  function widgets(blocks) { return blocks.filter(isWidget); }

  // The live body with only its changed top-level blocks replaced by the
  // conversion's. prefix and suffix count the blocks kept from live, and
  // replaced counts the conversion's blocks put between them. compare is
  // the patched body with the conversion's widgets in place of the live
  // ones, which is what a hash of the local conversion's body checks. body
  // is null when the change would add or drop a widget.
  function splice(live, conv) {
    var L = live.content, C = conv.content, p = 0, q = 0;
    while (p < L.length && p < C.length && same(L[p], C[p])) p++;
    while (q < L.length - p && q < C.length - p && same(L[L.length - 1 - q], C[C.length - 1 - q])) q++;
    var oldMiddle = L.slice(p, L.length - q), newMiddle = C.slice(p, C.length - q);
    var kept = widgets(oldMiddle);
    var out = { prefix: p, suffix: q, removed: oldMiddle.length, replaced: newMiddle.length, body: null, compare: null };
    if (kept.length !== widgets(newMiddle).length) return out;
    var w = 0;
    var middle = newMiddle.map(function (n) { return isWidget(n) ? kept[w++] : n; });
    var content = L.slice(0, p).concat(middle, L.slice(L.length - q));
    var body = {}, compare = {};
    Object.keys(live).forEach(function (k) { body[k] = live[k]; compare[k] = live[k]; });
    body.content = content;
    compare.content = content.map(function (n, i) { return isWidget(n) ? C[i] : n; });
    out.body = body;
    out.compare = compare;
    return out;
  }

  // Each figure name the converter reads from md, in document order. The
  // converter itself finds them, so no pattern here can disagree with it.
  function figureNames(md) {
    var names = [];
    var record = new Proxy({}, {
      get: function (_, name) {
        names.push(String(name));
        return { url: "", width: 0, height: 0, bytes: 0 };
      },
    });
    M2S.convert(md, record);
    return names;
  }
  function imageNodes(n, out) {
    out = out || [];
    if (n && n.type === "image2") out.push(n);
    ((n && n.content) || []).forEach(function (c) { imageNodes(c, out); });
    return out;
  }
  // The images map M2S.convert reads, built from the draft that holds md's
  // conversion. A string says why it could not be built.
  function imagesFromDraft(md, live) {
    var names = figureNames(md), nodes = imageNodes(live), map = {};
    if (names.length !== nodes.length) {
      return "the base Markdown names " + names.length + " figures and the draft holds " + nodes.length;
    }
    for (var i = 0; i < names.length; i++) {
      var a = nodes[i].attrs || {};
      var entry = { url: a.src, width: a.width, height: a.height, bytes: a.bytes };
      if (Object.prototype.hasOwnProperty.call(map, names[i]) && M2S.canon(map[names[i]]) !== M2S.canon(entry)) {
        return "the figure " + names[i] + " appears twice with different images";
      }
      map[names[i]] = entry;
    }
    return map;
  }

  // The first reason cfg cannot be used, or null.
  function badConfig(cfg) {
    if (!cfg || typeof cfg !== "object") return "no configuration";
    if (!DRAFT.test(String(cfg.draft))) return "draft is not a numeric id";
    if (!POST.test(String(cfg.post))) return "post is not a blog/*.md path";
    if (!COMMIT.test(String(cfg.commit))) return "commit is not a full sha";
    if (!COMMIT.test(String(cfg.base))) return "base is not a full sha";
    var e = cfg.expect || {};
    for (var i = 0; i < EXPECTED.length; i++) {
      if (!HASH.test(String(e[EXPECTED[i]]))) return "expect." + EXPECTED[i] + " is not 8 to 64 hex digits";
    }
    if (e.liveBody !== undefined && !HASH.test(String(e.liveBody))) return "expect.liveBody is not 8 to 64 hex digits";
    if (cfg.images !== undefined && (!cfg.images || typeof cfg.images !== "object")) return "images is not a map";
    return null;
  }

  // Why the draft cannot be written without the owner, or null. A read of an
  // unpublished draft has post_date null and no postSchedules, as the
  // owner's notes record. A read with no post_date at all is refused too,
  // since it cannot say.
  function published(d) {
    if (!Object.prototype.hasOwnProperty.call(d, "post_date")) return "the draft does not say whether it is published";
    if (d.post_date !== null) return "the draft is published";
    if (Array.isArray(d.postSchedules) && d.postSchedules.length) return "the draft is scheduled";
    return null;
  }

  function defaultIo() {
    return {
      fetch: function (url, init) { return fetch(url, init); },
      sha: async function (s) {
        var d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
        return Array.from(new Uint8Array(d)).map(function (b) { return b.toString(16).padStart(2, "0"); }).join("");
      },
    };
  }

  // Runs the checks in order and writes only when every one passes and
  // cfg.write is true. io replaces fetch and sha256 in the tests.
  async function syncTo(cfg, io) {
    io = io || defaultIo();
    var out = {};
    var bad = badConfig(cfg);
    if (bad) { out.refused = bad; return out; }
    var e = cfg.expect;
    var draftUrl = "/api/v1/drafts/" + cfg.draft;
    var hashes = async function (s, want) { return (await io.sha(s)).indexOf(want) === 0; };
    var text = async function (url) {
      var r = await io.fetch(url, { cache: "no-store" });
      return r.ok ? await r.text() : null;
    };
    // The draft and its parsed body, or null when either cannot be read.
    var readDraft = async function () {
      try {
        var r = await io.fetch(draftUrl, { cache: "no-store" });
        if (!r.ok) return null;
        var d = await r.json();
        return { d: d, body: JSON.parse(d.draft_body) };
      } catch (err) { return null; }
    };

    var md = await text(RAW + cfg.commit + "/" + cfg.post);
    var baseMd = await text(RAW + cfg.base + "/" + cfg.post);
    var first = await readDraft();
    if (md === null) { out.refused = "a read failed: the Markdown at commit"; return out; }
    if (baseMd === null) { out.refused = "a read failed: the Markdown at base"; return out; }
    if (first === null) { out.refused = "a read failed: the draft"; return out; }
    var d = first.d, live = first.body;
    var hold = published(d);
    if (hold) { out.refused = hold; return out; }
    out.mdOk = await hashes(md, e.md);
    if (!out.mdOk) { out.refused = "the Markdown"; return out; }
    if (e.liveBody !== undefined) {
      out.liveOk = await hashes(M2S.canon(live), e.liveBody);
      if (!out.liveOk) { out.refused = "the live body moved from its baseline"; return out; }
    }

    var held, images, conv, base;
    try {
      held = imagesFromDraft(baseMd, live);
      if (typeof held === "string") { out.refused = held; return out; }
      // The base converts with the images the draft holds, and commit with
      // those plus what cfg.images adds or replaces.
      images = {};
      [held, cfg.images || {}].forEach(function (m) { Object.keys(m).forEach(function (k) { images[k] = m[k]; }); });
      var missing = figureNames(md).filter(function (n) { return !Object.prototype.hasOwnProperty.call(images, n); });
      if (missing.length) { out.refused = "no image for " + missing.join(", ") + ": pass it in images"; return out; }
      conv = M2S.convert(md, images);
      base = M2S.convert(baseMd, held);
    } catch (err) {
      out.refused = "conversion failed: " + message(err);
      return out;
    }
    out.images = Object.keys(images).length;
    out.convOk = await hashes(M2S.canon(conv), e.conversion);
    if (!out.convOk) { out.refused = "the conversion"; return out; }
    out.baseOk = sameBlocks(live.content, base.body.content);
    if (!out.baseOk) { out.refused = "the live draft differs from the base commit's conversion"; return out; }

    var s = splice(live, conv.body);
    out.prefix = s.prefix;
    out.suffix = s.suffix;
    out.removed = s.removed;
    out.replaced = s.replaced;
    out.blocks = conv.body.content.length;
    out.titleSame = d.draft_title === conv.title;
    out.subtitleSame = d.draft_subtitle === conv.subtitle;
    if (!s.body) { out.refused = "the change adds or drops a widget"; return out; }
    out.patchOk = await hashes(M2S.canon(s.compare), e.body);
    out.walkOk = await hashes(M2S.walkLines(s.body).join("\n"), e.walk);
    if (!out.patchOk || !out.walkOk) { out.refused = "the patched body"; return out; }
    if (out.removed === 0 && out.replaced === 0) { out.unchanged = true; return out; }
    if (cfg.write !== true) { out.dryRun = true; return out; }

    var again = await readDraft();
    if (again === null || again.d.draft_updated_at !== d.draft_updated_at || again.d.draft_body !== d.draft_body) {
      out.refused = "the draft moved";
      return out;
    }
    try {
      var r = await io.fetch(draftUrl, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ draft_body: JSON.stringify(s.body) }),
      });
      out.put = r.status;
      if (!r.ok) { out.failed = "the write returned " + r.status; return out; }
      var back = await readDraft();
      if (back === null) { out.failed = "the read-back failed"; return out; }
      // The body sent already walked to e.walk, so an exact match carries it.
      out.readBack = M2S.canon(back.body) === M2S.canon(s.body);
      out.updatedChanged = back.d.draft_updated_at !== d.draft_updated_at;
      if (!out.readBack) { out.failed = "the read-back does not match what was sent"; return out; }
      // The next sync's liveBody. It is the local body_sha256 when the draft's
      // widgets are the converter's, and differs when the editor rewrote them.
      var after = await io.sha(M2S.canon(back.body));
      out.bodyAfter = after.slice(0, 12);
      out.backIsConversion = after.indexOf(e.body) === 0;
    } catch (err) {
      out.failed = "after the write began: " + message(err);
    }
    return out;
  }

  return {
    syncTo: syncTo, splice: splice, same: same, isWidget: isWidget,
    imagesFromDraft: imagesFromDraft, figureNames: figureNames, badConfig: badConfig,
  };
})();
