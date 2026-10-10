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
// md2substack.py's docstring lists what each Markdown shape becomes, including
// pipe tables, headings of two to six hashes and linked images, and states the
// rule that turns a table cell into LaTeX. The two files differ only in
// language.
//
// The regular expressions here are the Python's, character for character, and
// avoid ".", "\d", "\s" and "\w", which mean different things in the two
// languages. Lines and cells are trimmed of ASCII whitespace only, never with
// trim(), which also strips U+FEFF where Python's strip() does not.
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
// does. The change for issue 472 then taught both copies pipe tables, headings
// of four to six hashes and linked images, unescaped the subtitle, and made the
// two copies agree on whitespace and digits outside ASCII. The review of that
// change matched GitHub on where a table ends and on a delimiter row of bare
// hyphens, gave the caret a width, collapsed whitespace in cells, and stopped
// two kinds of image line from throwing.
var M2S = (function () {
  var LINK = { target: "_blank", rel: "noopener noreferrer nofollow", "class": null };
  var WIDGET = {
    type: "subscribeWidget",
    attrs: { url: "%%checkout_url%%", text: "Subscribe", language: "en" },
    content: [{ type: "ctaCaption", content: [{ type: "text", text: "baowebdev is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber." }] }]
  };
  var HEADING = /^(#{2,6}) /;
  var IMAGE = /^!\[([^\n]*)\]\(([^)]+)\)$/;
  var LINKED_IMAGE = /^\[!\[([^\n]*)\]\(([^)]+)\)\]\(([^)]+)\)$/;
  var LIST_ITEM = /^([0-9]+\. |- )/;
  var NESTED_ITEM = /^   ([0-9]+\. |- )/;
  // An image or a linked image opens a block only as the whole line, so opensBlock tests those.
  var BLOCK_START = /^(#{2,6} |```|[0-9]+\. |- )/;
  var DELIMITER_CELL = /^:?-+:?$/;
  var SPACE_RUN = /[ \t]+/g;
  var ASCII_PUNCTUATION = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~";
  var LATEX_SPECIAL = {
    "$": "\\$", "%": "\\%", "&": "\\&", "#": "\\#", "_": "\\_", "{": "\\{", "}": "\\}",
    "\\": "\\backslash", "~": "{\\sim}", "^": "{\\hat{\\ }}"
  };
  function clone(x) { return JSON.parse(JSON.stringify(x)); }
  // ASCII whitespace only, the set WHITESPACE names in the Python.
  function trim(s) { return s.replace(/^[ \t\n\r\f\v]+|[ \t\n\r\f\v]+$/g, ""); }
  // The backslash comes off \~ and \$ in body text and subtitle alike.
  function unescape(t) { return t.split("\\~").join("~").split("\\$").join("$"); }
  function text(t, marks) {
    var node = { type: "text", text: unescape(t) };
    if (marks.length) node.marks = marks.slice();
    return node;
  }
  function inline(s, marks) {
    marks = marks || [];
    var re = /\*\*([^\n]+?)\*\*|\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*([^\n]+?)\*/g;
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
  // The index of the line closing the fence opened on line i, the same as
  // _fence_end in the Python. A fence left open would otherwise loop forever.
  function fenceEnd(lines, i) {
    var j = i + 1;
    while (j < lines.length && lines[j] !== "```") j++;
    if (j === lines.length) throw new Error("unterminated fence opened on line " + (i + 1) + ": " + lines[i]);
    return j;
  }
  // A table row's cells, untrimmed, split at each | with no backslash before it.
  function cells(row) {
    var s = trim(row);
    if (s.indexOf("|") === 0) s = s.slice(1);
    if (s.slice(-1) === "|" && s.slice(-2) !== "\\|") s = s.slice(0, -1);
    var out = [], cell = "";
    for (var k = 0; k < s.length; k++) {
      if (s[k] === "|" && (k === 0 || s[k - 1] !== "\\")) { out.push(cell); cell = ""; }
      else cell += s[k];
    }
    out.push(cell);
    return out;
  }
  // Each column's alignment when a table starts on line i, else null. A
  // delimiter row with no | and no : is bare hyphens, which GitHub reads as a
  // heading underline, so it starts no table.
  function tableColumns(lines, i) {
    if (lines[i].indexOf("|") !== 0 || i + 1 >= lines.length) return null;
    var below = lines[i + 1];
    if (below.indexOf("|") < 0 && below.indexOf(":") < 0) return null;
    var marks = cells(below).map(trim);
    if (!marks.every(function (c) { return DELIMITER_CELL.test(c); })) return null;
    if (cells(lines[i]).length !== marks.length) return null;
    return marks.map(function (c) {
      return c[0] === ":" && c[c.length - 1] === ":" ? "c" : c[c.length - 1] === ":" ? "r" : "l";
    });
  }
  function closingRun(s, j, run) {
    while (j < s.length) {
      if (s[j] === "`") {
        var k = j;
        while (k < s.length && s[k] === "`") k++;
        if (k - j === run) return j;
        j = k;
      } else j++;
    }
    return -1;
  }
  function stripMarkup(s) {
    var re = /!\[([^\]]*)\]\([^)]+\)|\[((?:!\[[^\]]*\]\([^)]+\)|[^\]])+)\]\([^)]+\)|\*\*([^\n]+?)\*\*|\*([^\n]+?)\*/g;
    return s.replace(re, function (m, a, b, c, d) {
      return stripMarkup([a, b, c, d].filter(function (g) { return g !== undefined; })[0]);
    });
  }
  // A table cell's plain text, as cell_text reads it in the Python.
  function cellText(cell) {
    var held = [], out = [], i = 0;
    function hold(t) { out.push("\\`" + held.length + "`"); held.push(t); }
    while (i < cell.length) {
      var ch = cell[i];
      if (ch === "\\" && i + 1 < cell.length && ASCII_PUNCTUATION.indexOf(cell[i + 1]) >= 0) {
        hold(cell[i + 1]); i += 2;
      } else if (ch === "`") {
        var j = i;
        while (j < cell.length && cell[j] === "`") j++;
        var close = closingRun(cell, j, j - i);
        if (close < 0) { hold(cell.slice(i, j)); i = j; }
        else {
          var code = cell.slice(j, close);
          if (code.slice(0, 1) === " " && code.slice(-1) === " " && /[^ ]/.test(code)) code = code.slice(1, -1);
          hold(code);
          i = close + (j - i);
        }
      } else { out.push(ch); i++; }
    }
    var t = stripMarkup(out.join("")).replace(/\\`([0-9]+)`/g, function (m, n) { return held[Number(n)]; });
    return t.replace(SPACE_RUN, " ");
  }
  function cellLatex(t) {
    var out = [], run = "";
    for (var k = 0; k < t.length; k++) {
      if (Object.prototype.hasOwnProperty.call(LATEX_SPECIAL, t[k])) {
        if (run) { out.push("\\text{" + run + "}"); run = ""; }
        out.push(LATEX_SPECIAL[t[k]]);
      } else run += t[k];
    }
    if (run) out.push("\\text{" + run + "}");
    return out.join("");
  }
  function tableLatex(header, rows, columns) {
    function row(cs) {
      cs = cs.concat(columns.map(function () { return ""; })).slice(0, columns.length);
      return cs.map(function (c) { return cellLatex(cellText(trim(c).split("\\|").join("|"))); }).join(" & ");
    }
    var out = ["\\begin{array}{" + columns.join("|") + "}", row(header) + " \\\\ \\hline"];
    rows.forEach(function (r, k) { out.push(row(r) + (k < rows.length - 1 ? " \\\\" : "")); });
    out.push("\\end{array}");
    return out.join("\n");
  }
  function opensBlock(line) {
    return BLOCK_START.test(line) || IMAGE.test(line) || LINKED_IMAGE.test(line);
  }
  function startsBlock(lines, i) {
    return opensBlock(lines[i]) || tableColumns(lines, i) !== null;
  }
  // A captioned image, and the index of the line after it and its caption.
  function figure(lines, i, images, alt, path, href) {
    var img = images[path.split("/").pop()];
    var node = { type: "captionedImage", content: [{ type: "image2", attrs: {
      src: img.url, srcNoWatermark: null, fullscreen: null, imageSize: null, height: img.height, width: img.width,
      resizeWidth: null, bytes: img.bytes, alt: alt, title: null, type: "image/png", href: href, belowTheFold: false,
      topImage: false, internalRedirect: null, isProcessing: false, align: null, offset: false } }] };
    var k = i + 1; while (k < lines.length && !trim(lines[k])) k++;
    // A figure on the post's last non-blank line has no caption to look for.
    var cap = k < lines.length ? lines[k] : "";
    if (cap[0] === "*" && cap[cap.length - 1] === "*" && cap.indexOf("**") !== 0) {
      node.content.push({ type: "caption", content: inline(cap.slice(1, -1)) });
      return [node, k + 1];
    }
    return [node, i + 1];
  }
  function convert(md, images) {
    var lines = md.split("\n");
    var title = trim(lines[0].replace(/^# /, ""));
    var subtitle = unescape(trim(lines[2]).replace(/^\*+|\*+$/g, ""));
    var body = [], i = 3, nHeading = 0, eq = 0, made;
    while (i < lines.length) {
      var line = lines[i];
      if (!trim(line)) { i++; continue; }
      var heading = line.match(HEADING), image = line.match(IMAGE), linked = line.match(LINKED_IMAGE);
      var columns = tableColumns(lines, i);
      if (heading) {
        var level = heading[1].length - 1;
        if (level === 1) {
          nHeading++;
          if (nHeading === 2) body.push(clone(WIDGET));
        }
        body.push({ type: "heading", attrs: { textAlign: null, level: level }, content: inline(trim(line.slice(heading[0].length))) }); i++;
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
      } else if (image) {
        made = figure(lines, i, images, image[1], image[2], null);
        body.push(made[0]); i = made[1];
      } else if (linked) {
        var target = linked[3];
        var href = /^https?:\/\//.test(target) ? target : null;
        made = figure(lines, i, images, linked[1], linked[2], href);
        body.push(made[0]); i = made[1];
      } else if (columns) {
        // As on GitHub, every line up to a blank one or one that opens another block is a row.
        var end = i + 2;
        while (end < lines.length && trim(lines[end]) && !opensBlock(lines[end])) end++;
        eq++;
        body.push({ type: "latex_block", attrs: {
          persistentExpression: tableLatex(cells(line), lines.slice(i + 2, end).map(cells), columns),
          id: "EQSTAT" + (eq < 10 ? "0" : "") + eq } });
        i = end;
      } else if (LIST_ITEM.test(line)) {
        var ordered = line.indexOf("- ") !== 0, items = [];
        while (i < lines.length && LIST_ITEM.test(lines[i])) {
          items.push([lines[i].replace(LIST_ITEM, ""), []]); i++;
          while (i < lines.length && NESTED_ITEM.test(lines[i])) {
            items[items.length - 1][1].push([lines[i].indexOf("   - ") === 0, lines[i].replace(NESTED_ITEM, "")]); i++;
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
        while (i < lines.length && trim(lines[i]) && !startsBlock(lines, i)) { buf.push(lines[i]); i++; }
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
