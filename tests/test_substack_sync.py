"""The in-page sync of a Substack draft, ``substack_sync.js``.

A session syncs a draft by calling ``SYNC.syncTo`` in a page on the
publication. The function replaces only the top-level blocks that changed and
refuses to write whenever a hash or a comparison says the write could lose an
edit the owner made in the editor. Those refusals are what make the write safe
to send without a dry run, so each one is pinned here, along with each way a
write can fail after it starts.

No test talks to Substack. Each case runs the function against a fake ``fetch``
that serves the Markdown at two commits and one draft, and records every
request. A test reads what the function returned and what it sent. A few more
cases call ``SYNC.splice`` directly on blocks no post produces.

The fixture post has ten blocks once converted, with the two subscribe
widgets the converter adds at indices 5 and 9. The live draft's widgets carry
a url the editor wrote, a different one for each, so a test can tell which
widget went where.

The JavaScript runs under the engine ``tests/test_substack_converter.py``
picks, node or ``osascript -l JavaScript``. JavaScriptCore has no
``crypto.subtle``, so the driver hashes with its own SHA-256, and
``test_the_driver_hash_is_sha256`` checks it against ``hashlib``. The page's
own ``crypto.subtle`` path is the one part no test runs.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from tests.test_substack_converter import SKILL_DIR, _engine, m2s

SYNC_JS = SKILL_DIR / "substack_sync.js"
RAW = "https://raw.githubusercontent.com/l3a0/quantitative-trading/"
POST = "blog/sync-fixture.md"
DRAFT_ID = "123456"
BASE_SHA = "a" * 40
NEW_SHA = "b" * 40
IMAGES = {
    "sync_chart.png": {
        "url": "https://example.invalid/sync_chart.png",
        "width": 1300,
        "height": 754,
        "bytes": 4321,
    }
}
NEW_IMAGE = {
    "url": "https://example.invalid/sync_new.png",
    "width": 680,
    "height": 320,
    "bytes": 999,
}
REDRAWN = {
    "sync_chart.png": {
        "url": "https://example.invalid/sync_chart_v2.png",
        "width": 1300,
        "height": 800,
        "bytes": 5000,
    }
}
# What the editor writes into a widget, which differs from the converter's.
EDITOR_WIDGET_URL = "https://example.invalid/subscribe"

BASE_MD = """# A sync fixture

*A subtitle for the sync tests.*

The opening paragraph.

## First section

A paragraph in the first section.

![A chart](../docs/figures/sync_chart.png)

*The chart's caption.*

The paragraph that changes.

## Second section

The paragraph before the end.

The last paragraph.
"""

ONE_PARAGRAPH = BASE_MD.replace("The paragraph that changes.", "The paragraph that changed, once.")
AROUND_A_WIDGET = ONE_PARAGRAPH.replace("## Second section", "## Second part")
NO_SECOND_HEADING = ONE_PARAGRAPH.replace("## Second section", "Second section, as a paragraph.")
# The same paragraph twice in a row, which a prefix and a suffix could both claim.
REPEATED_PARAGRAPH = BASE_MD.replace(
    "The opening paragraph.\n", "The opening paragraph.\n\nThe opening paragraph.\n"
)
NEW_FIGURE = ONE_PARAGRAPH + "\n![A second chart](../docs/figures/sync_new.png)\n"
FIGURE_TWICE = BASE_MD + "\n![The chart again](../docs/figures/sync_chart.png)\n"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _body(md: str, images: dict = IMAGES) -> dict:
    return m2s.convert(md, images)["body"]


def _live_body(md: str = BASE_MD) -> dict:
    """The base conversion as the editor stores it, each widget's url rewritten."""
    body = _body(md)
    for i, block in enumerate(body["content"]):
        if block["type"] == "subscribeWidget":
            block["attrs"]["url"] = f"{EDITOR_WIDGET_URL}-{i}"
    return body


def _draft(body: dict, **fields) -> dict:
    """The draft as GET /api/v1/drafts/<id> returns an unpublished one."""
    return {
        "draft_title": "A sync fixture",
        "draft_subtitle": "A subtitle for the sync tests.",
        "draft_updated_at": "2026-10-21T10:00:00.000Z",
        "draft_body": json.dumps(body),
        "post_date": None,
        "postSchedules": [],
        **fields,
    }


def _expect(md: str, live: dict, images: dict = IMAGES) -> dict:
    """The hashes a session takes from --summary and from its notes."""
    summary = m2s.summary(m2s.convert(md, images), md.encode("utf-8"))
    return {
        "md": summary["md_sha256"],
        "conversion": summary["conversion_sha256"][:8],
        "liveBody": _sha(m2s.canonical(live)),
        "body": summary["body_sha256"],
        "walk": summary["walk_sha256"][:12],
    }


def _case(
    name: str,
    md: str = ONE_PARAGRAPH,
    live: dict | None = None,
    write: bool = True,
    expect: dict | None = None,
    draft: dict | None = None,
    images: dict = IMAGES,
    base_md: str = BASE_MD,
    **extra,
) -> dict:
    live = live if live is not None else _live_body()
    cfg = {
        "draft": DRAFT_ID,
        "post": POST,
        "base": BASE_SHA,
        "commit": NEW_SHA,
        "expect": {**_expect(md, live, images), **(expect or {})},
        "write": write,
    }
    cfg.update(extra.pop("cfg", {}))
    cfg["expect"] = {k: v for k, v in cfg["expect"].items() if v is not None}
    files = {RAW + BASE_SHA + "/" + POST: base_md, RAW + NEW_SHA + "/" + POST: md}
    case = {"name": name, "cfg": cfg, "files": files, "draft": draft or _draft(live)}
    case.update(extra)
    return case


def _highlighted() -> dict:
    """The live body with a highlight the owner added to the last paragraph."""
    body = _live_body()
    body["content"][8]["content"][0]["marks"] = [
        {"type": "highlight", "attrs": {"color": "yellow"}}
    ]
    return body


def _without_figure() -> dict:
    body = _live_body()
    del body["content"][3]
    return body


def _figure_twice_live() -> dict:
    """A draft of FIGURE_TWICE whose two images are different uploads."""
    body = _live_body(FIGURE_TWICE)
    body["content"][-2]["content"][0]["attrs"]["src"] = "https://example.invalid/other.png"
    return body


BAD_CONFIGS = {
    "short hash": {"expect": {**_expect(ONE_PARAGRAPH, _live_body()), "walk": "abc1234"}},
    "missing base": {"base": None},
    "draft id with letters": {"draft": "12a"},
    "post outside blog": {"post": "../blog/sync-fixture.md"},
    "short commit": {"commit": "b" * 39},
    "upper-case hash": {"expect": {**_expect(ONE_PARAGRAPH, _live_body()), "md": "ABCDEF12"}},
    "short liveBody": {"expect": {**_expect(ONE_PARAGRAPH, _live_body()), "liveBody": "abc"}},
    "empty draft id": {"draft": ""},
    "draft id reaching another path": {"draft": "1/../../posts/123"},
    "post climbing out of blog": {"post": "blog/a/../b.md"},
    "post with a trailing path": {"post": "blog/sync-fixture.md/x"},
    "long commit": {"commit": "b" * 41},
    "hash over 64 digits": {"expect": {**_expect(ONE_PARAGRAPH, _live_body()), "md": "a" * 65}},
    "hash with a letter past f": {
        "expect": {**_expect(ONE_PARAGRAPH, _live_body()), "md": "z" + "a" * 8}
    },
    **{
        f"empty {key}": {"expect": {**_expect(ONE_PARAGRAPH, _live_body()), key: ""}}
        for key in ("md", "conversion", "body", "walk", "liveBody")
    },
    "images not a map": {"images": "sync_chart.png"},
}

# Each refusal: its case, the reason it returns, and the flag it sets false.
REFUSALS = [
    ("live body off its baseline", "the live body moved from its baseline", "liveOk"),
    ("owner highlight", "the live draft differs from the base commit's conversion", "baseOk"),
    ("change drops a widget", "the change adds or drops a widget", None),
    ("draft moves before the write", "the draft moved", None),
    ("draft body moves before the write", "the draft moved", None),
    ("conversion hash differs", "the conversion", "convOk"),
    ("markdown hash differs", "the Markdown", "mdOk"),
    ("markdown hash matches mid-way", "the Markdown", "mdOk"),
    (
        "live body shorter than the base",
        "the live draft differs from the base commit's conversion",
        "baseOk",
    ),
    ("patched body hash differs", "the patched body", "patchOk"),
    ("patched walk hash differs", "the patched body", "walkOk"),
    (
        "figure missing from the draft",
        "the base Markdown names 1 figures and the draft holds 0",
        None,
    ),
    (
        "figure twice with two uploads",
        "the figure sync_chart.png appears twice with different images",
        None,
    ),
    ("new figure with no image", "no image for sync_new.png: pass it in images", None),
    ("markdown not found", "a read failed: the Markdown at commit", None),
    ("base markdown not found", "a read failed: the Markdown at base", None),
    ("draft body not json", "a read failed: the draft", None),
    ("draft not found", "a read failed: the draft", None),
    ("published", "the draft is published", None),
    ("scheduled", "the draft is scheduled", None),
    ("no post_date", "the draft does not say whether it is published", None),
]


def _cases() -> list[dict]:
    live = _live_body()
    no_post_date = _draft(live)
    del no_post_date["post_date"]
    cases = [
        _case("writes one paragraph"),
        _case("dry run", write=False),
        _case("write must be true", cfg={"write": "yes"}),
        _case("no liveBody", expect={"liveBody": None}),
        _case("live body off its baseline", expect={"liveBody": _sha("another body")}),
        _case("owner highlight", live=_highlighted()),
        _case("widget inside the change", md=AROUND_A_WIDGET),
        _case("repeated paragraph", md=REPEATED_PARAGRAPH),
        _case("converter widgets", live=_body(BASE_MD)),
        _case("change drops a widget", md=NO_SECOND_HEADING),
        _case("draft moves before the write", moveAfterRead=1),
        _case("draft body moves before the write", moveBodyAfterRead=1),
        _case(
            "title and subtitle differ",
            draft=_draft(live, draft_title="Another", draft_subtitle=""),
        ),
        _case("conversion hash differs", expect={"conversion": "0" * 8}),
        _case("markdown hash differs", expect={"md": "0" * 64}),
        _case(
            "markdown hash matches mid-way",
            expect={"md": _expect(ONE_PARAGRAPH, live)["md"][4:16]},
        ),
        _case("live body shorter than the base", live={**live, "content": live["content"][:-1]}),
        _case(
            "one figure used twice",
            md=FIGURE_TWICE.replace("The paragraph that changes.", "Changed."),
            base_md=FIGURE_TWICE,
            live=_live_body(FIGURE_TWICE),
        ),
        _case("patched body hash differs", expect={"body": "0" * 8}),
        _case("patched walk hash differs", expect={"walk": "0" * 8}),
        _case("nothing changed", md=BASE_MD, cfg={"commit": BASE_SHA}),
        _case("figure missing from the draft", live=_without_figure()),
        _case(
            "figure twice with two uploads",
            md=FIGURE_TWICE,
            base_md=FIGURE_TWICE,
            live=_figure_twice_live(),
        ),
        _case(
            "new figure with no image", md=NEW_FIGURE, images={**IMAGES, "sync_new.png": NEW_IMAGE}
        ),
        _case(
            "new figure passed in",
            md=NEW_FIGURE,
            images={**IMAGES, "sync_new.png": NEW_IMAGE},
            cfg={"images": {"sync_new.png": NEW_IMAGE}},
        ),
        _case("redrawn figure passed in", images=REDRAWN, cfg={"images": REDRAWN}),
        _case("markdown not found", missing=RAW + NEW_SHA + "/" + POST),
        _case("base markdown not found", missing=RAW + BASE_SHA + "/" + POST),
        _case("draft body not json", draft=_draft(live, draft_body="not json")),
        _case("draft not found", missing="/api/v1/drafts/" + DRAFT_ID),
        _case("published", draft=_draft(live, post_date="2026-10-02T12:03:26.000Z")),
        _case(
            "scheduled", draft=_draft(live, postSchedules=[{"trigger_at": "2026-11-01T12:00:00Z"}])
        ),
        _case("no post_date", draft=no_post_date),
        _case("write fails", putStatus=500),
        _case("read-back differs", alterOnPut=True),
        _case("read-back fails", failReadAfterPut=True),
        _case("write keeps its timestamp", keepUpdatedAt=True),
    ]
    cases += [_case("bad config: " + name, cfg=change) for name, change in BAD_CONFIGS.items()]
    return cases


def _block(kind: str, text: str) -> dict:
    """A top-level block for the splice cases, a paragraph or a widget."""
    if kind == "W":
        return {"type": "subscribeWidget", "attrs": {"url": text}}
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


# Called on SYNC.splice directly. The first has two widgets inside the change,
# which no committed post produces, so only here is their order observable.
SPLICES = [
    (
        "two widgets inside the change",
        [("P", "p"), ("W", "live-a"), ("W", "live-b"), ("P", "q")],
        [("P", "p2"), ("W", "conv"), ("W", "conv"), ("P", "q2")],
    ),
    ("a widget appears", [("P", "p"), ("P", "q")], [("P", "p"), ("W", "conv"), ("P", "q")]),
]


def _splices() -> list[list]:
    return [
        [
            name,
            {"type": "doc", "content": [_block(*b) for b in live]},
            {"type": "doc", "content": [_block(*b) for b in conv]},
        ]
        for name, live, conv in SPLICES
    ]


SHA_INPUTS = ["", "abc", "é and ∑ and 𝔼", "x" * 55, "x" * 56, "x" * 64, "x" * 119, "y" * 1000]

# A SHA-256 for engines with no crypto.subtle, over the string's UTF-8 bytes.
SHA256_JS = """
function __sha256(str) {
  var bytes = unescape(encodeURIComponent(str)), n = bytes.length, words = [], i, t;
  var K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2];
  var H = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
  var total = (((n + 8) >> 6) + 1) * 16;
  for (i = 0; i < total; i++) words[i] = 0;
  for (i = 0; i < n; i++) words[i >> 2] |= bytes.charCodeAt(i) << (24 - (i % 4) * 8);
  words[n >> 2] |= 0x80 << (24 - (n % 4) * 8);
  words[total - 1] = n * 8;
  var rot = function (x, r) { return (x >>> r) | (x << (32 - r)); };
  var W = [];
  for (var j = 0; j < total; j += 16) {
    var a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
    for (t = 0; t < 64; t++) {
      if (t < 16) W[t] = words[j + t] | 0;
      else W[t] = (W[t - 16] + (rot(W[t - 15], 7) ^ rot(W[t - 15], 18) ^ (W[t - 15] >>> 3))
        + W[t - 7] + (rot(W[t - 2], 17) ^ rot(W[t - 2], 19) ^ (W[t - 2] >>> 10))) | 0;
      var t1 = (h + (rot(e, 6) ^ rot(e, 11) ^ rot(e, 25)) + ((e & f) ^ (~e & g)) + K[t] + W[t]) | 0;
      var t2 = ((rot(a, 2) ^ rot(a, 13) ^ rot(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) | 0;
      h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b; b = a; a = (t1 + t2) | 0;
    }
    H[0] = (H[0] + a) | 0; H[1] = (H[1] + b) | 0; H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0;
    H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
  }
  return H.map(function (x) { return ("0000000" + (x >>> 0).toString(16)).slice(-8); }).join("");
}
"""

# Appended after md2substack.js, substack_sync.js and SHA256_JS. It runs each
# case against a fake server and prints one line per case. Percent signs and
# the three line separators Python splits on are written as JSON escapes, as
# tests/test_substack_converter.py's driver writes them, because osascript's
# console.log reads its argument as a format string.
DRIVER = """
(async function () {
  var emit = function (line) {
    var escape = function (c) {
      return "\\\\u" + ("000" + c.charCodeAt(0).toString(16)).slice(-4);
    };
    line = line.replace(/[%\\u0085\\u2028\\u2029]/g, escape);
    if (typeof console !== "undefined" && console.log) { console.log(line); } else { print(line); }
  };
  var reply = function (status, body) {
    return { ok: status >= 200 && status < 300, status: status,
      text: async function () { return body; }, json: async function () { return body; } };
  };
  emit("SYNC_SHA " + JSON.stringify(__SHA_INPUTS.map(__sha256)));
  __SPLICES.forEach(function (c) {
    emit("SPLICE_RESULT " + JSON.stringify({ name: c[0], out: SYNC.splice(c[1], c[2]) }));
  });
  for (var k = 0; k < __CASES.length; k++) {
    var c = __CASES[k];
    var state = JSON.parse(JSON.stringify(c.draft)), reads = 0, log = [];
    var put = null, written = false, inits = [];
    var draftUrl = "/api/v1/drafts/" + c.cfg.draft;
    var io = {
      sha: async function (s) { return __sha256(s); },
      fetch: async function (url, init) {
        var method = (init && init.method) || "GET";
        log.push(method + " " + url);
        inits.push(init || null);
        if (url === draftUrl && method === "PUT") {
          put = JSON.parse(init.body).draft_body;
          if (c.putStatus) return reply(c.putStatus, null);
          written = true;
          var stored = JSON.parse(put);
          if (c.alterOnPut) stored.content.pop();
          state.draft_body = JSON.stringify(stored);
          if (!c.keepUpdatedAt) state.draft_updated_at = "2026-10-21T10:05:00.000Z";
          return reply(200, null);
        }
        if (url === draftUrl && url !== c.missing) {
          if (written && c.failReadAfterPut) return reply(500, { error: "failed" });
          reads++;
          var snapshot = JSON.parse(JSON.stringify(state));
          if (c.moveAfterRead === reads) state.draft_updated_at = "2026-10-21T10:01:00.000Z";
          if (c.moveBodyAfterRead === reads) {
            state.draft_body = JSON.stringify(JSON.parse(state.draft_body));
          }
          return reply(200, snapshot);
        }
        if (url !== c.missing && Object.prototype.hasOwnProperty.call(c.files, url)) {
          return reply(200, c.files[url]);
        }
        return reply(404, url === draftUrl ? { error: "not found" } : "404: Not Found");
      },
    };
    var result = { name: c.name, error: null, log: log };
    try {
      result.out = await SYNC.syncTo(c.cfg, io);
    } catch (e) { result.error = String(e) + (e && e.stack ? "\\n" + e.stack : ""); }
    result.put = put;
    result.inits = inits;
    emit("SYNC_RESULT " + JSON.stringify(result));
  }
})();
void 0;
"""


@pytest.fixture(scope="module")
def run(tmp_path_factory: pytest.TempPathFactory) -> dict:
    """Every case's result, and the driver's hashes, from one engine run."""
    engine = _engine()
    cases = _cases()
    script = (
        (SKILL_DIR / "md2substack.js").read_text(encoding="utf-8")
        + "\n"
        + SYNC_JS.read_text(encoding="utf-8")
        + SHA256_JS
        + f"\nvar __SHA_INPUTS = {json.dumps(SHA_INPUTS, ensure_ascii=False)};\n"
        + f"var __CASES = {json.dumps(cases, ensure_ascii=False)};\n"
        + f"var __SPLICES = {json.dumps(_splices(), ensure_ascii=False)};\n"
        + DRIVER
    )
    runner = Path(tmp_path_factory.mktemp("substack_sync")) / "run.js"
    runner.write_text(script, encoding="utf-8")
    try:
        done = subprocess.run(
            [*engine, str(runner)], capture_output=True, text=True, timeout=120, check=False
        )
    except subprocess.TimeoutExpired:
        pytest.fail("substack_sync.js did not finish within 120 seconds")
    output = done.stdout + done.stderr
    assert done.returncode == 0, output[-2000:]
    results, hashes, splices = {}, None, {}
    for line in output.splitlines():
        if line.startswith("SYNC_RESULT "):
            result = json.loads(line[len("SYNC_RESULT ") :])
            results[result["name"]] = result
        elif line.startswith("SPLICE_RESULT "):
            result = json.loads(line[len("SPLICE_RESULT ") :])
            splices[result["name"]] = result["out"]
        elif line.startswith("SYNC_SHA "):
            hashes = json.loads(line[len("SYNC_SHA ") :])
    assert set(results) == {c["name"] for c in cases}, output[-2000:]
    for result in results.values():
        assert result["error"] is None, result["error"]
    assert set(splices) == {name for name, _, _ in SPLICES}, output[-2000:]
    return {"cases": results, "sha": hashes, "splices": splices}


def _methods(result: dict) -> list[str]:
    return [entry.split(" ", 1)[0] for entry in result["log"]]


def _put(run: dict, name: str) -> dict:
    return json.loads(run["cases"][name]["put"])


def test_the_driver_hash_is_sha256(run: dict) -> None:
    """Every expectation below is a hashlib digest, so the driver's must agree."""
    assert run["sha"] == [_sha(s) for s in SHA_INPUTS]


def test_a_changed_paragraph_replaces_that_block_only(run: dict) -> None:
    out = run["cases"]["writes one paragraph"]["out"]
    assert "refused" not in out and "failed" not in out
    for check in (
        "mdOk",
        "liveOk",
        "convOk",
        "baseOk",
        "patchOk",
        "walkOk",
        "titleSame",
        "subtitleSame",
    ):
        assert out[check] is True, check
    assert (out["prefix"], out["removed"], out["replaced"], out["suffix"]) == (4, 1, 1, 5)
    assert out["blocks"] == 10
    assert out["images"] == 1
    expected = _live_body()
    expected["content"][4] = _body(ONE_PARAGRAPH)["content"][4]
    assert _put(run, "writes one paragraph") == expected
    assert (out["put"], out["readBack"], out["updatedChanged"]) == (200, True, True)
    assert out["bodyAfter"] == _sha(m2s.canonical(expected))[:12]
    assert out["backIsConversion"] is False


def test_a_draft_with_the_converters_widgets_reads_back_as_the_conversion(run: dict) -> None:
    """With no widget rewritten, the next baseline is the local body_sha256."""
    out = run["cases"]["converter widgets"]["out"]
    assert out["backIsConversion"] is True
    assert out["bodyAfter"] == _sha(m2s.canonical(_body(ONE_PARAGRAPH)))[:12]


def test_the_write_reads_twice_before_it_and_once_after(run: dict) -> None:
    draft = "/api/v1/drafts/" + DRAFT_ID
    assert run["cases"]["writes one paragraph"]["log"] == [
        "GET " + RAW + NEW_SHA + "/" + POST,
        "GET " + RAW + BASE_SHA + "/" + POST,
        "GET " + draft,
        "GET " + draft,
        "PUT " + draft,
        "GET " + draft,
    ]


def test_without_a_live_body_hash_the_base_comparison_stands_in(run: dict) -> None:
    """A record with no body hash, or a hidden bodyAfter, still syncs."""
    out = run["cases"]["no liveBody"]["out"]
    assert "liveOk" not in out
    assert out["baseOk"] is True and out["put"] == 200
    assert _put(run, "no liveBody") == _put(run, "writes one paragraph")


def test_widgets_match_whatever_their_attributes(run: dict) -> None:
    """The suffix runs through both widgets though the editor rewrote their url.

    The write keeps the editor's widgets, each in its own place, rather than
    the converter's.
    """
    put = _put(run, "writes one paragraph")
    assert [put["content"][i]["attrs"]["url"] for i in (5, 9)] == [
        f"{EDITOR_WIDGET_URL}-5",
        f"{EDITOR_WIDGET_URL}-9",
    ]


def test_a_widget_inside_the_change_keeps_the_live_one(run: dict) -> None:
    out = run["cases"]["widget inside the change"]["out"]
    assert "refused" not in out
    assert (out["prefix"], out["removed"], out["replaced"], out["suffix"]) == (4, 3, 3, 3)
    expected = _live_body()
    new = _body(AROUND_A_WIDGET)
    expected["content"][4] = new["content"][4]
    expected["content"][6] = new["content"][6]
    assert _put(run, "widget inside the change") == expected


def test_widgets_inside_the_change_keep_their_live_order(run: dict) -> None:
    out = run["splices"]["two widgets inside the change"]
    assert (out["prefix"], out["removed"], out["replaced"], out["suffix"]) == (0, 4, 4, 0)
    assert out["body"]["content"] == [
        _block("P", "p2"),
        _block("W", "live-a"),
        _block("W", "live-b"),
        _block("P", "q2"),
    ]
    assert [b["attrs"]["url"] for b in out["compare"]["content"][1:3]] == ["conv", "conv"]


def test_a_widget_that_appears_leaves_no_body(run: dict) -> None:
    out = run["splices"]["a widget appears"]
    assert out["body"] is None and out["compare"] is None


def test_a_repeated_paragraph_is_inserted_once(run: dict) -> None:
    """The prefix and the suffix never claim the same live block.

    Without that limit the suffix runs back through the first paragraph, the
    two meet with nothing between them, and the call reports no change.
    """
    out = run["cases"]["repeated paragraph"]["out"]
    assert (out["prefix"], out["removed"], out["replaced"], out["suffix"]) == (1, 0, 1, 9)
    live = _live_body()
    assert _put(run, "repeated paragraph") == {
        **live,
        "content": [
            live["content"][0],
            _body(REPEATED_PARAGRAPH)["content"][1],
            *live["content"][1:],
        ],
    }


def test_a_title_or_subtitle_difference_is_reported_and_left_alone(run: dict) -> None:
    """A post whose subtitle is over 255 units keeps it blank, and the write sends the body only."""
    result = run["cases"]["title and subtitle differ"]
    assert (result["out"]["titleSame"], result["out"]["subtitleSame"]) == (False, False)
    assert result["out"]["put"] == 200
    assert _put(run, "title and subtitle differ") == _put(run, "writes one paragraph")


def test_a_figure_can_be_added_or_replaced_by_passing_it_in(run: dict) -> None:
    added = run["cases"]["new figure passed in"]["out"]
    assert added["put"] == 200 and added["images"] == 2
    assert (
        _put(run, "new figure passed in")["content"][9]
        == _body(NEW_FIGURE, {**IMAGES, "sync_new.png": NEW_IMAGE})["content"][9]
    )
    redrawn = run["cases"]["redrawn figure passed in"]["out"]
    assert (redrawn["prefix"], redrawn["removed"], redrawn["replaced"]) == (3, 2, 2)
    assert (
        _put(run, "redrawn figure passed in")["content"][3]
        == _body(ONE_PARAGRAPH, REDRAWN)["content"][3]
    )


def test_one_figure_used_twice_with_one_upload_syncs(run: dict) -> None:
    out = run["cases"]["one figure used twice"]["out"]
    assert "refused" not in out
    assert out["images"] == 1 and out["put"] == 200


def test_every_read_skips_the_cache_and_the_write_is_json(run: dict) -> None:
    """A cached draft could pass the re-read before the write and hide an owner edit."""
    result = run["cases"]["writes one paragraph"]
    for entry, init in zip(result["log"], result["inits"], strict=True):
        if entry.startswith("GET "):
            assert init == {"cache": "no-store"}, entry
        else:
            assert init["headers"] == {"Content-Type": "application/json"}, entry


def test_without_write_true_it_only_reports(run: dict) -> None:
    for name in ("dry run", "write must be true"):
        result = run["cases"][name]
        assert result["out"]["dryRun"] is True, name
        assert result["out"]["patchOk"] is True, name
        assert "PUT" not in _methods(result), name
        assert result["put"] is None, name


@pytest.mark.parametrize(("name", "reason", "flag"), REFUSALS)
def test_each_refusal_sends_no_write(run: dict, name: str, reason: str, flag: str | None) -> None:
    result = run["cases"][name]
    assert result["out"]["refused"] == reason
    if flag:
        assert result["out"][flag] is False
    assert "PUT" not in _methods(result)
    assert result["put"] is None


def test_a_held_draft_is_refused_before_anything_is_hashed(run: dict) -> None:
    for name in ("published", "scheduled", "no post_date"):
        assert "mdOk" not in run["cases"][name]["out"], name


def test_a_live_body_off_its_baseline_stops_before_converting(run: dict) -> None:
    """The baseline check comes first, so nothing after it runs on a moved draft."""
    out = run["cases"]["live body off its baseline"]["out"]
    assert "convOk" not in out and "baseOk" not in out


def test_the_owner_highlight_passes_the_baseline_and_still_stops(run: dict) -> None:
    """A highlight the last sync kept matches the baseline, so only the base comparison stops it.

    Block 8 differs from every conversion, so without that comparison every
    sync would copy it from the conversion and drop the highlight.
    """
    out = run["cases"]["owner highlight"]["out"]
    assert out["liveOk"] is True and out["convOk"] is True


@pytest.mark.parametrize(
    ("name", "failed"),
    [
        ("write fails", "the write returned 500"),
        ("read-back differs", "the read-back does not match what was sent"),
        ("read-back fails", "the read-back failed"),
    ],
)
def test_a_failed_write_says_so_and_gives_no_baseline(run: dict, name: str, failed: str) -> None:
    """A session records bodyAfter as the next baseline, so a failure must not carry one."""
    out = run["cases"][name]["out"]
    assert out["failed"] == failed
    assert "refused" not in out
    assert "bodyAfter" not in out and "backIsConversion" not in out
    assert "PUT" in _methods(run["cases"][name])


def test_a_write_that_leaves_the_timestamp_says_so(run: dict) -> None:
    out = run["cases"]["write keeps its timestamp"]["out"]
    assert out["readBack"] is True and out["updatedChanged"] is False


def test_nothing_changed_writes_nothing(run: dict) -> None:
    result = run["cases"]["nothing changed"]
    assert result["out"]["unchanged"] is True
    assert (result["out"]["removed"], result["out"]["replaced"]) == (0, 0)
    assert "PUT" not in _methods(result)


@pytest.mark.parametrize("name", sorted(BAD_CONFIGS))
def test_a_bad_configuration_is_refused_before_any_request(run: dict, name: str) -> None:
    result = run["cases"]["bad config: " + name]
    assert result["out"]["refused"]
    assert result["log"] == []
