// The in-page copy of md2substack.py, which converts a blog post's Markdown
// into the ProseMirror JSON tree Substack stores as a draft's body.
//
// Why a second copy exists. A draft is created or synced from inside the
// signed-in Substack page, because the API it calls needs that page's session.
// The page cannot read this checkout, and typing a converted tree of 30 to 40
// KB into a script by hand has gone wrong before. So the page fetches the
// Markdown from raw.githubusercontent.com at a pinned commit and converts it
// here, and the script refuses to write unless the result hashes to what
// md2substack.py produced locally. Both files must give the same tree for
// every post, and tests/test_substack_converter.py checks that they do.
//
// Usage: paste this file at the top of the script sent to the page, then call
// M2S.convert(markdown, images), M2S.canon(value) and M2S.walkLines(node).
// md2substack.py's docstring lists what each Markdown shape becomes, and the
// two files differ only in language.
//
// Where this came from. No repository held this file before. Sessions wrote
// it in their scratchpads from 2026-10-03 and copied it from one scratchpad
// to the next. A snapshot of every surviving copy taken on 2026-10-10 found
// three versions, each a strict superset of the one before. This is the
// newest, sha1 42e86a5d, last changed on 2026-10-10 to turn \$ into $ as the
// Python copy does. The older two, sha1 c1d4c4e8 and 761a4a8a, lacked that
// change, and the oldest also lacked the branch that turns a non-math fence
// into a code block. It was checked in on a branch from da64a66. The copy
// changed three things.
//
// 1. These comments were rewritten. The code was left as it ran.
// 2. canon and walkLines were added from the in-page check scripts, where each
//    session retyped them, to match canonical and walk_lines in the Python.
// 3. M2S now returns them beside convert.
//
// After the check-in, fenceEnd replaced the two fence loops, which looped
// forever on a fence with no closing line. It throws instead, as the Python
// does.
var M2S = (function () {
  var LINK = { target: "_blank", rel: "noopener noreferrer nofollow", "class": null };
  var WIDGET = {
    type: "subscribeWidget",
    attrs: { url: "%%checkout_url%%", text: "Subscribe", language: "en" },
    content: [{ type: "ctaCaption", content: [{ type: "text", text: "baowebdev is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber." }] }]
  };
  function clone(x) { return JSON.parse(JSON.stringify(x)); }
  function text(t, marks) {
    t = t.split("\\~").join("~").split("\\$").join("$");
    var node = { type: "text", text: t };
    if (marks.length) node.marks = marks.slice();
    return node;
  }
  function inline(s, marks) {
    marks = marks || [];
    var re = /\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*(.+?)\*/g;
    var out = [], pos = 0, m;
    while ((m = re.exec(s)) !== null) {
      if (m.index > pos) out.push(text(s.slice(pos, m.index), marks));
      if (m[1] !== undefined) out = out.concat(inline(m[1], marks.concat([{ type: "strong" }])));
      else if (m[2] !== undefined) {
        var link = { type: "link", attrs: Object.assign({ href: m[3] }, LINK) };
        out = out.concat(inline(m[2], [link].concat(marks)));
      } else if (m[4] !== undefined) out.push(text(m[4], marks.concat([{ type: "code" }])));
      else out = out.concat(inline(m[5], marks.concat([{ type: "em" }])));
      pos = re.lastIndex;
    }
    if (pos < s.length) out.push(text(s.slice(pos), marks));
    return out.filter(function (n) { return n.text; });
  }
  function para(s) { return { type: "paragraph", attrs: { textAlign: null }, content: inline(s) }; }
  var LISTSTART = /^(\d+\. |- )/;
  // The index of the line closing the fence opened on line i, the same as
  // _fence_end in the Python. A fence left open would otherwise loop forever.
  function fenceEnd(lines, i) {
    var j = i + 1;
    while (j < lines.length && lines[j] !== "```") j++;
    if (j === lines.length) throw new Error("unterminated fence opened on line " + (i + 1) + ": " + lines[i]);
    return j;
  }
  function convert(md, images) {
    var lines = md.split("\n");
    var title = lines[0].replace(/^# /, "").trim();
    var subtitle = lines[2].trim().replace(/^\*+|\*+$/g, "");
    var body = [], i = 3, nHeading = 0, eq = 0;
    while (i < lines.length) {
      var line = lines[i];
      if (!line.trim()) { i++; continue; }
      if (line.indexOf("### ") === 0) {
        body.push({ type: "heading", attrs: { textAlign: null, level: 2 }, content: inline(line.slice(4).trim()) }); i++;
      } else if (line.indexOf("## ") === 0) {
        nHeading++;
        if (nHeading === 2) body.push(clone(WIDGET));
        body.push({ type: "heading", attrs: { textAlign: null, level: 1 }, content: inline(line.slice(3).trim()) }); i++;
      } else if (line.indexOf("```math") === 0) {
        var j = fenceEnd(lines, i);
        eq++;
        body.push({ type: "latex_block", attrs: { persistentExpression: lines.slice(i + 1, j).join("\n"), id: "EQSTAT" + (eq < 10 ? "0" : "") + eq } });
        i = j + 1;
      } else if (line.indexOf("```") === 0) {
        // Any other fence, such as ```latex showing an equation's source, is a plain code block.
        var jj = fenceEnd(lines, i);
        var code = lines.slice(i + 1, jj).join("\n");
        var cb = { type: "highlighted_code_block", attrs: { language: "plaintext", nodeId: null } };
        if (code) cb.content = [{ type: "text", text: code }];
        body.push(cb);
        i = jj + 1;
      } else if (line.indexOf("![") === 0) {
        var mm = line.match(/^!\[(.*)\]\(([^)]+)\)$/);
        var alt = mm[1], path = mm[2], img = images[path.split("/").pop()];
        var node = { type: "captionedImage", content: [{ type: "image2", attrs: {
          src: img.url, srcNoWatermark: null, fullscreen: null, imageSize: null, height: img.height, width: img.width,
          resizeWidth: null, bytes: img.bytes, alt: alt, title: null, type: "image/png", href: null, belowTheFold: false,
          topImage: false, internalRedirect: null, isProcessing: false, align: null, offset: false } }] };
        var k = i + 1; while (!lines[k].trim()) k++;
        var cap = lines[k];
        if (cap[0] === "*" && cap[cap.length - 1] === "*" && cap.indexOf("**") !== 0) {
          node.content.push({ type: "caption", content: inline(cap.slice(1, -1)) }); i = k + 1;
        } else i++;
        body.push(node);
      } else if (LISTSTART.test(line)) {
        var ordered = /^\d+\. /.test(line), items = [];
        while (i < lines.length && LISTSTART.test(lines[i])) {
          items.push([lines[i].replace(LISTSTART, ""), []]); i++;
          while (i < lines.length && /^   (\d+\. |- )/.test(lines[i])) {
            items[items.length - 1][1].push([lines[i].indexOf("   - ") === 0, lines[i].replace(/^   (\d+\. |- )/, "")]); i++;
          }
        }
        var li = items.map(function (it) {
          var content = [para(it[0])], sub = it[1];
          if (sub.length) {
            var subitems = sub.map(function (s) { return { type: "list_item", content: [para(s[1])] }; });
            if (sub[0][0]) content.push({ type: "bullet_list", content: subitems });
            else content.push({ type: "ordered_list", attrs: { start: 1, type: null, order: 1 }, content: subitems });
          }
          return { type: "list_item", content: content };
        });
        body.push(ordered ? { type: "ordered_list", attrs: { start: 1, type: null, order: 1 }, content: li } : { type: "bullet_list", content: li });
      } else {
        var buf = [line]; i++;
        while (i < lines.length && lines[i].trim() && !/^(### |## |```|!\[|\d+\. |- )/.test(lines[i])) { buf.push(lines[i]); i++; }
        body.push(para(buf.join(" ")));
      }
    }
    body.push(clone(WIDGET));
    return { title: title, subtitle: subtitle, body: { type: "doc", content: body } };
  }
  // Sorted keys and no added whitespace, the same string canonical() makes.
  function canon(x) {
    if (Array.isArray(x)) return "[" + x.map(canon).join(",") + "]";
    if (x && typeof x === "object") {
      return "{" + Object.keys(x).sort().map(function (k) { return JSON.stringify(k) + ":" + canon(x[k]); }).join(",") + "}";
    }
    return JSON.stringify(x);
  }
  // One line per text run, LaTeX block and image, the same lines walk_lines() makes.
  function walkLines(n, path, out) {
    path = path || ""; out = out || [];
    var t = n.type;
    if (t === "text") {
      var marks = (n.marks || []).map(function (m) { return m.type + (m.type === "link" ? ":" + m.attrs.href : ""); }).sort().join(",");
      out.push(path + "|" + marks + "|" + n.text);
    }
    if (t === "latex_block") out.push(path + "|latex|" + n.attrs.persistentExpression);
    if (t === "image2") out.push(path + "|img|" + n.attrs.src + "|" + n.attrs.alt);
    (n.content || []).forEach(function (c, i) { walkLines(c, path + "/" + i + (c.type || "").slice(0, 3), out); });
    return out;
  }
  return { convert: convert, canon: canon, walkLines: walkLines };
})();
