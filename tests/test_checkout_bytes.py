"""The committed vintages' bytes, held fixed against the checkout that writes them.

`data/checksums.sha256` records a sha256 for every committed vintage, and
[docs/design.md](../docs/design.md) makes those exact bytes the thing this repo
must not lose. A checksum is a claim about bytes, so it is a fact only while
the bytes a clone writes are the bytes that were committed. Git for Windows
defaults to `core.autocrlf=true`, which rewrites every line ending on checkout,
and nothing in such a clone reports it. `git status` reads clean while every
tracked file under `data/` differs from its committed blob, and
`shasum -a 256 -c checksums.sha256` fails on every vintage without opening one,
because the list it parses was rewritten too.

A runner on ubuntu never reproduces that rewrite, so no case below reads its own
working tree. The first has `git checkout-index` write what a converting
checkout would write into a scratch directory, under a `core.autocrlf` it sets
rather than inherits. The others
read the index, which no platform's checkout touches. All three answer the same
everywhere.

The three cases divide the work, and the division is what stops any one of them
holding the guard alone.

1. The byte sweep catches the rule going away or narrowing to a pattern that
   misses a file. It cannot carry the spelling, because `data/** text eol=lf`
   delivers identical bytes for content already stored as LF.
2. The attribute case carries the spelling. `text eol=lf` would let git strip
   the carriage returns out of a vintage that carries them, which turns a
   recorded hash into a false one and leaves no way back to the bytes.
3. The distribution case carries where the rule lives. Both of the others ask
   git what it resolves here, and git resolves an attribute from
   `.git/info/attributes` and from `core.attributesFile` as well as from the
   tracked file. Neither of those is cloned. Measured: moving the rule into
   `.git/info/attributes` leaves both of the other cases green while a clone of
   that tree loses every vintage.

Every case reads the index rather than `HEAD`. The recorder writes a vintage and
a run of the suite comes before the commit, so `HEAD:` holds no blob for a path
that is only staged.

`markdown_files` in `tests/support/markdown_sweep.py` asks git for its file set
the same way and counts untracked files on purpose. This sweep cannot. An
untracked file has no blob, so there is nothing for a checkout to write and
nothing to compare against.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from chan.paths import DATA_DIR, REPO_ROOT

# Derived rather than written as `data`, because `chan.paths` calls itself the
# single switch for where the vintages sit. A hard-coded pattern would be a
# second surface that has to move with it, and the vintages would land outside
# the attribute with this file still green.
DATA_PREFIX = DATA_DIR.relative_to(REPO_ROOT).as_posix()

ATTRIBUTES_FILE = ".gitattributes"
PROJECTION = f"{DATA_PREFIX}/checksums.sha256"

# A control for the byte sweep. The sweep asserts that nothing changes, which
# passes just as well when the conversion was never switched on, so it needs
# one path that does change. This one is tracked, textual and outside the
# attribute's reach, so a converting checkout rewrites it.
CONTROL = "README.md"

# The pattern has to cross a slash. `data/*` stops at the directory's own
# children, and git resolves an attribute for a path whether or not it exists,
# so probing costs nothing and catches the narrowing before a vintage lands
# under it.
NESTED_PROBE = f"{DATA_PREFIX}/nested/probe.csv"


def _git(*arguments: str, given: bytes | None = None) -> bytes:
    """Run git at the repository root, raising with the command when it fails."""
    command = ["git", "-C", str(REPO_ROOT), *arguments]
    result = subprocess.run(command, input=given, capture_output=True, check=False)
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"{' '.join(command)} failed in {REPO_ROOT}: {message}")
    return result.stdout


def _committed_data_paths() -> list[str]:
    """Every path under the data directory that a clone would receive."""
    listing = _git("ls-files", "-z", "--cached", "--", DATA_PREFIX)
    paths = sorted(name for name in listing.decode("utf-8").split("\0") if name)
    # A sweep over nothing passes every assertion below it. The projection is
    # the file `shasum -c` parses before it opens a vintage, so its presence is
    # what says the set is the one this file is about.
    assert PROJECTION in paths, (
        f"the sweep found {len(paths)} committed paths under {DATA_PREFIX}/ and {PROJECTION} "
        f"is not among them, so it is no longer reading the set this file is about. Found: "
        f"{', '.join(paths) or 'nothing'}"
    )
    return paths


def _staged_blobs(*paths: str) -> dict[str, str]:
    """The blob each path holds in the index, which is what a clone would receive."""
    listing = _git("ls-files", "-z", "--stage", "--", *paths).decode("utf-8")
    blobs = {}
    for record in listing.split("\0"):
        if record:
            meta, path = record.split("\t", 1)
            blobs[path] = meta.split()[1]
    return blobs


def _committed_bytes(*paths: str) -> dict[str, bytes]:
    """What the index holds for each path, read in one `git cat-file --batch` run.

    One process for the whole sweep rather than one per path. Unfiltered, the
    size each header reports is the size of the content that follows it, so
    the output splits cleanly. Under `--filters` it does not: the header keeps
    the stored size while the content is the converted one, 37,542 against
    38,229 bytes for `README.md` when this was written, which is why the
    converting half below goes through a checkout instead.
    """
    blobs = _staged_blobs(*paths)
    asked = [blobs[path] for path in paths]
    output = _git("cat-file", "--batch", given="".join(blob + "\n" for blob in asked).encode())
    contents, at = {}, 0
    for path in paths:
        end = output.index(b"\n", at)
        header = output[at:end].decode("utf-8").split()
        if len(header) != 3:
            raise RuntimeError(f"git cat-file could not read {path}: {' '.join(header)}")
        size = int(header[2])
        contents[path] = output[end + 1 : end + 1 + size]
        at = end + 1 + size + 1
    return contents


def _checkout_bytes(scratch: Path, *paths: str) -> dict[str, bytes]:
    """What a checkout carrying git's Windows default writes for each path.

    `git checkout-index` performs that checkout into `scratch` rather than
    being asked what it would write, so the conversion under test is the one a
    clone runs. It takes every path in one process. The sweep used to ask
    `git cat-file --filters` once per path, two processes a path at about 13 ms
    each, which was 0.81 s over the fifteen single-series vintages and 41.39 s
    once the 1,100 columns lifted from Chan's `.mat` files were in the index,
    measured on [issue 88](https://github.com/l3a0/quantitative-trading/issues/88).

    The control below and the sweep share this call, on purpose. A control
    reached by its own call proves the conversion is switched on somewhere
    rather than in the comparison that matters, so dropping the forced setting
    out of the sweep would leave the control green.
    """
    _git(
        "-c",
        "core.autocrlf=true",
        "checkout-index",
        "-z",
        "--stdin",
        f"--prefix={scratch}/",
        given="".join(path + "\0" for path in paths).encode("utf-8"),
    )
    return {path: (scratch / path).read_bytes() for path in paths}


def _attribute_states(attribute: str, *paths: str) -> dict[str, str]:
    """What git resolves `attribute` to for each path, read from the index."""
    report = _git("check-attr", "--cached", attribute, "--", *paths).decode("utf-8")
    states = {}
    for line in report.splitlines():
        if line:
            path, _, state = line.rsplit(": ", 2)
            states[path] = state
    return states


def test_a_checkout_converting_line_endings_still_writes_the_committed_bytes(
    tmp_path: Path,
) -> None:
    paths = _committed_data_paths()
    written = _checkout_bytes(tmp_path, CONTROL, *paths)
    stored = _committed_bytes(CONTROL, *paths)
    assert written[CONTROL] != stored[CONTROL], (
        f"a converting checkout leaves {CONTROL} unchanged, so the comparison below is "
        f"asserting nothing. Either the forced core.autocrlf is no longer reaching git, or "
        f"a rule now covers {CONTROL} as well, in which case pick a control outside it."
    )

    rewritten = [path for path in paths if written[path] != stored[path]]

    named = ", ".join(rewritten)
    assert not rewritten, (
        f"a clone made with core.autocrlf=true writes different bytes for {len(rewritten)} "
        f"of {len(paths)} committed paths under {DATA_PREFIX}/, so every sha256 recorded for "
        f"them stops describing the file on disk. The cause is the checkout's line-ending "
        f"conversion rather than the data, and the fix is the .gitattributes rule holding "
        f"'{DATA_PREFIX}/** -text'. Rewritten: {named}"
    )


def test_the_committed_attribute_forbids_conversion_rather_than_picking_an_ending() -> None:
    paths = _committed_data_paths()
    states = _attribute_states("text", *paths, NESTED_PROBE)
    wrong = sorted(path for path, state in states.items() if state != "unset")

    named = ", ".join(f"{path} is {states[path]}" for path in wrong)
    assert not wrong, (
        f"{len(wrong)} of {len(paths) + 1} paths under {DATA_PREFIX}/ do not carry the text "
        f"attribute as 'unset', which is what forbids git converting them. 'set' means the "
        f"rule was written as 'text eol=lf', which lets git strip the carriage returns out "
        f"of a vintage that carries them and makes its recorded sha256 false. 'unspecified' "
        f"means no committed rule reaches the path. A narrower pattern, an unstaged "
        f".gitattributes and a rule that stops at this directory's own children all produce "
        f"it, and {NESTED_PROBE} is the probe that catches the last of those. Wrong: {named}"
    )


def test_the_attribute_leaves_a_vintage_its_diff() -> None:
    """`binary` would hold the bytes too, and the register cut it for this.

    It is a macro for `-text`, `-diff` and `-merge`, so it protects the bytes
    and takes the diff with them. `data/README.md` calls replacing a vintage a
    deliberate act with a visible cost, and the diff is that cost.
    """
    paths = _committed_data_paths()
    states = _attribute_states("diff", *paths)
    silenced = sorted(path for path, state in states.items() if state == "unset")

    named = ", ".join(silenced)
    assert not silenced, (
        f"{len(silenced)} of {len(paths)} committed paths under {DATA_PREFIX}/ have their "
        f"diff turned off, which is what 'binary' does on top of holding the bytes. "
        f"Replacing a vintage would stop rendering as a diff, and that diff is how a "
        f"replacement gets read. Silenced: {named}"
    )


def test_the_rule_lives_in_a_blob_a_clone_receives() -> None:
    """Git resolves an attribute from files a clone never gets.

    `.git/info/attributes` and `core.attributesFile` both feed `check-attr` and
    `checkout-index`, and neither is cloned. Measured: moving the rule into
    `.git/info/attributes` leaves the two cases above green while a clone made
    from that tree fails every vintage. So the rule has to be read out of the
    index rather than asked of git.
    """
    tracked = _git("ls-files", "--cached", "--", ATTRIBUTES_FILE).decode("utf-8").split()
    assert tracked == [ATTRIBUTES_FILE], (
        f"{ATTRIBUTES_FILE} is not in the index, so no clone receives it. Git may still "
        f"resolve the rule here out of .git/info/attributes or core.attributesFile, neither "
        f"of which is cloned, which is how this guard reads healthy while every clone of it "
        f"loses the vintages."
    )

    blob = _git("cat-file", "blob", f":{ATTRIBUTES_FILE}").decode("utf-8")
    covering = [
        line
        for line in blob.splitlines()
        if line.split()[:1] == [f"{DATA_PREFIX}/**"] and "-text" in line.split()[1:]
    ]
    assert covering, (
        f"the committed {ATTRIBUTES_FILE} carries no line reading '{DATA_PREFIX}/** -text', "
        f"so whatever holds the bytes here is not what a clone receives. Committed:\n{blob}"
    )
