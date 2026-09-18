"""The committed vintages' bytes, held fixed against the checkout that writes them.

`data/checksums.sha256` records a sha256 for every committed vintage, and
[docs/design.md](../docs/design.md) makes those exact bytes the thing this repo
must not lose. A checksum is a claim about bytes, so it is a fact only while
the bytes a clone writes are the bytes that were committed. Git for Windows
defaults to `core.autocrlf=true`, which rewrites every line ending on checkout,
and nothing in such a clone reports it. `git status` reads clean while all
eleven tracked files under `data/` differ from their committed blobs, and
`shasum -a 256 -c checksums.sha256` fails on all eight vintages without opening
one, because the list it parses was rewritten too.

A runner on ubuntu never reproduces that rewrite, so neither case below reads
its own working tree. `git cat-file --filters` asks git what a checkout would
write, under a `core.autocrlf` these cases set rather than inherit, so both
answer the same on every platform.

The two cases divide the work. The first compares stored bytes against checkout
bytes, which catches the guard going away or narrowing to a pattern that misses
a file. The second reads the attribute itself, because `data/** text eol=lf`
delivers identical bytes for content already stored as LF. That spelling would
pass the first case while granting git permission to strip the carriage returns
out of a vintage that carries them, which turns a recorded hash into a false
one and leaves no way back to the bytes.

Both read the index rather than `HEAD`. The recorder writes a vintage and a run
of the suite comes before the commit, so `HEAD:` holds no blob for a path that
is only staged. `--cached` carries the same reasoning from the other side. Git
resolves attributes from the working tree, so a `.gitattributes` written and
never added passes a plain `check-attr` while a clone receives nothing.

`markdown_files` in `tests/support/markdown_sweep.py` asks git for its file set
the same way and counts untracked files on purpose. This sweep cannot. An
untracked file has no blob, so there is nothing for a checkout to write and
nothing to compare against.
"""

from __future__ import annotations

import subprocess

from chan.paths import DATA_DIR, REPO_ROOT

# Derived rather than written as `data`, because `chan.paths` calls itself the
# single switch for where the vintages sit. A hard-coded pattern would be a
# second surface that has to move with it, and the vintages would land outside
# the attribute with this file still green.
DATA_PREFIX = DATA_DIR.relative_to(REPO_ROOT).as_posix()


def _git(*arguments: str) -> bytes:
    """Run git at the repository root, raising with the command when it fails."""
    command = ["git", "-C", str(REPO_ROOT), *arguments]
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"{' '.join(command)} failed in {REPO_ROOT}: {message}")
    return result.stdout


def _committed_data_paths() -> list[str]:
    """Every path under the data directory that a clone would receive."""
    listing = _git("ls-files", "-z", "--cached", "--", DATA_PREFIX)
    return sorted(name for name in listing.decode("utf-8").split("\0") if name)


def test_a_checkout_converting_line_endings_still_writes_the_committed_bytes() -> None:
    paths = _committed_data_paths()
    rewritten = [
        path
        for path in paths
        if _git("-c", "core.autocrlf=true", "cat-file", "--filters", f":{path}")
        != _git("cat-file", "blob", f":{path}")
    ]

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
    report = _git("check-attr", "--cached", "text", "--", *paths).decode("utf-8")
    states = dict(
        (line.rsplit(": ", 2)[0], line.rsplit(": ", 2)[2]) for line in report.splitlines() if line
    )
    wrong = sorted(path for path, state in states.items() if state != "unset")

    named = ", ".join(f"{path} is {states[path]}" for path in wrong)
    assert states and not wrong, (
        f"{len(wrong)} of {len(paths)} committed paths under {DATA_PREFIX}/ do not carry the "
        f"text attribute as 'unset', which is what forbids git converting them. 'set' means "
        f"the rule was written as 'text eol=lf', which lets git strip the carriage returns "
        f"out of a vintage that carries them and makes its recorded sha256 false. "
        f"'unspecified' means no committed rule reaches the path, which a narrower pattern "
        f"and an unstaged .gitattributes both produce. Wrong: {named}"
    )
