"""Move the retired artifact board's judgement onto GitHub, once.

Until issue 533 the build board's judgement lived only in a claude.ai
artifact's database: the priority order, the decompose verdicts, the sessions
at work, what each card waits on and each card's kind. ``build_board.py`` now
reads each of them from GitHub, as a label, a native "blocked by" link, a line
in an issue body or a line in an owner's comment. This script copies the
artifact's values into those homes, so the board built from GitHub draws what
the artifact board drew on the day it retired.

It works from a readback of the artifact database, the six JSON files that an
``ArtifactData`` list of the ``board`` collection writes with ``out_dir`` set.
Nothing here reads the artifact itself, which only the ``ArtifactData`` tool
can.

1. ``plan`` prints every write the readback calls for that GitHub does not
   already hold, and every disagreement it will not resolve on its own. It
   writes nothing.
2. ``apply`` makes those writes, and appends each one to a log as it lands.
3. ``undo`` reverses the writes a log records, newest first.
4. ``compare`` lists where a ``board.json`` the generator built differs from
   the readback, field by field, leaving out the fields that have no home on
   GitHub on purpose.

The writes go to the live tracker, so ``apply`` runs as the last step before
the pull request that retires the artifact board merges, and only once the
owner has approved it in chat. It skips anything already present, so a second
run changes nothing. If it stops partway, or the merge does not follow, the
log is what ``undo`` reverses, so the tracker never holds half of a second
record while sessions still write the first.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_board as bb  # noqa: E402

SECTIONS = ("state", "prs", "working", "planned", "next", "tracker")

# The fields the artifact board held that have no home on GitHub, and why.
# `why` and `title` in `next` and `note` in `planned` were never rendered, and
# `what` in `working` now renders as the kind of session. `label` is the issue
# title, and 23 cards carried a rewrite that no issue is retitled to match.
UNHOMED = {
    "next": {"why", "title"},
    "planned": {"note"},
    "working": {"what"},
    "tracker": {"label"},
    "prs": set(),
}


def comparable_labels(labels: list[str] | None) -> list[str]:
    """A card's label chips less the ones the move changes on purpose.

    The generator leaves the board's own ``band:N`` and ``working:`` labels off
    a card's chips, and the backfill adds ``decision`` to eight cards that never
    carried it. Every other chip must match, so a card that lost one is found.
    """
    return sorted(
        x for x in labels or [] if not bb.BAND.match(x) and x not in bb.WORKING and x != "decision"
    )


Run = Callable[[list[str]], str]


def gh(args: list[str]) -> str:
    """Runs one ``gh`` command and returns what it printed, or stops the run."""
    done = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise bb.BoardError(f"gh {' '.join(args[:3])} failed: {done.stderr.strip()}")
    return done.stdout


def read_readback(folder: Path) -> dict[str, dict]:
    """The artifact's six documents, with the database's own fields dropped."""
    docs = {}
    for name in SECTIONS:
        doc = json.loads((folder / f"{name}.json").read_text(encoding="utf-8"))
        docs[name] = {k: v for k, v in doc.items() if not k.startswith("__")}
    return docs


def read_github(gql: bb.Gql, repo: str) -> dict[int, dict]:
    """Every open issue's labels, body, blockers, sub-issues and owner verdicts."""
    owner, name = repo.split("/", 1)
    out = {}
    for issue in bb._top_pages(gql, bb.ISSUES_QUERY, owner, name, "issues"):
        labels = bb._all_nodes(gql, issue["id"], "labels", issue["labels"])
        blockers = bb._all_nodes(gql, issue["id"], "blockedBy", issue["blockedBy"])
        comments = bb._all_nodes(gql, issue["id"], "issueComments", issue["issueComments"])
        out[issue["number"]] = {
            "labels": {lb["name"] for lb in labels},
            "body": issue.get("body") or "",
            # A link to another repository's issue has a number that means
            # nothing here, so it neither counts as present nor blocks a write.
            "blocked_by": {
                b["number"]
                for b in blockers
                if (b.get("repository") or {}).get("nameWithOwner") == repo
            },
            "sub_issues": issue["subIssues"]["totalCount"],
            "verdict": bb.latest_verdict(comments),
        }
    return out


def order_text(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)


def plan(docs: dict[str, dict], live: dict[int, dict]) -> tuple[list[dict], list[str]]:
    """The writes the readback calls for, and what it will not resolve itself.

    Each write is a dict naming its ``op`` and ``issue``. A card that is no
    longer open is skipped and noted, because the board draws only open issues.
    """
    writes: list[dict] = []
    notes: list[str] = []

    def add_label(n: int, label: str) -> None:
        if n not in live:
            notes.append(f"#{n} is not open, so {label} is not set")
        elif label not in live[n]["labels"]:
            writes.append({"op": "label", "issue": n, "label": label})

    def add_line(n: int, line: str) -> None:
        if n not in live:
            notes.append(f"#{n} is not open, so its line {line!r} is not written")
        elif line not in bb.unfenced(live[n]["body"]).splitlines():
            writes.append({"op": "line", "issue": n, "line": line})

    planned = {p["n"]: p for p in docs["planned"]["items"]}
    tracker = {c["n"]: c for c in docs["tracker"]["items"]}

    for x in docs["next"]["items"]:
        n = x["issue"]
        add_label(n, f"band:{x['band']}")
        if "order" in x:
            existing = bb.ORDER.findall(bb.unfenced(live.get(n, {}).get("body", "")))
            line = f"Board order: {order_text(x['order'])}"
            if existing and line.split(": ", 1)[1] not in existing:
                notes.append(f"#{n} already carries an order line {existing}, so {line!r} waits")
            else:
                add_line(n, line)
        kind = tracker.get(n, {}).get("kind")
        p = planned.get(n)
        derived = p["ready"] if p else ("decide" if kind == "decision" else "plan")
        if derived != x["ready"]:
            notes.append(
                f"#{n}: the artifact's next entry says {x['ready']}, "
                f"and the rule gives {derived} from "
                + ("its planned entry" if p else f"its kind, {kind}")
            )

    for n, p in planned.items():
        if n not in live:
            notes.append(f"#{n} is not open, so its verdict is not recorded")
        elif live[n]["verdict"] != (p["ready"], p["passes"]):
            writes.append({"op": "verdict", "issue": n, "ready": p["ready"], "passes": p["passes"]})

    for w in docs["working"]["items"]:
        add_label(w["n"], f"working:{w.get('kind') or 'decompose'}")

    for n, c in sorted(tracker.items()):
        if n not in live:
            notes.append(f"#{n} is a card on the artifact board but not an open issue")
            continue
        # The decision label is the one kind label the backfill sets, so the
        # kind GitHub will give is read as if it were already there.
        labels = set(live[n]["labels"])
        if c["kind"] == "decision":
            add_label(n, "decision")
            labels.add("decision")
        expected = bb.card_kind(sorted(labels), live[n]["sub_issues"])
        if expected != c["kind"]:
            notes.append(f"#{n}: the artifact's kind is {c['kind']}, and GitHub gives {expected}")
        for b in c["needs"]:
            if b not in live:
                notes.append(f"#{n} needs #{b}, which is not open, so no link is added")
            elif b not in live[n]["blocked_by"]:
                writes.append({"op": "link", "issue": n, "blocker": b})
        after = c.get("after") or []
        if after:
            add_line(n, "Board after: " + ", ".join(f"#{b}" for b in after))

    for n in sorted(set(live) - set(tracker)):
        notes.append(f"#{n} is open but has no card on the artifact board")
    return writes, notes


def verdict_comment(ready: str, passes: int) -> str:
    return (
        "## Board verdict\n\n"
        "Recorded from the retired artifact board's `planned` section, when the "
        "build board moved onto GitHub under #533.\n\n"
        f"Board verdict: {ready} after {passes} pass{'es' if passes != 1 else ''}\n"
    )


def apply_write(run: Run, repo: str, w: dict) -> dict:
    """Makes one write and returns what ``undo`` needs to reverse it."""
    n = w["issue"]
    if w["op"] == "label":
        run(["issue", "edit", str(n), "--repo", repo, "--add-label", w["label"]])
        return w
    if w["op"] == "line":
        body = json.loads(run(["api", f"repos/{repo}/issues/{n}", "--jq", "{body: .body}"]))
        text = (body["body"] or "").rstrip("\n")
        run(
            [
                "api",
                "--method",
                "PATCH",
                f"repos/{repo}/issues/{n}",
                "-f",
                f"body={text}\n\n{w['line']}\n",
            ]
        )
        return w
    if w["op"] == "verdict":
        made = json.loads(
            run(
                [
                    "api",
                    "--method",
                    "POST",
                    f"repos/{repo}/issues/{n}/comments",
                    "-f",
                    f"body={verdict_comment(w['ready'], w['passes'])}",
                    "--jq",
                    "{id: .id}",
                ]
            )
        )
        return {**w, "comment": made["id"]}
    if w["op"] == "link":
        blocker = json.loads(
            run(["api", f"repos/{repo}/issues/{w['blocker']}", "--jq", "{id: .id}"])
        )
        run(
            [
                "api",
                "--method",
                "POST",
                f"repos/{repo}/issues/{n}/dependencies/blocked_by",
                "-F",
                f"issue_id={blocker['id']}",
            ]
        )
        return {**w, "blocker_id": blocker["id"]}
    raise bb.BoardError(f"unknown write {w['op']}")


def undo_write(run: Run, repo: str, w: dict) -> None:
    """Reverses one logged write."""
    n = w["issue"]
    if w["op"] == "label":
        run(["issue", "edit", str(n), "--repo", repo, "--remove-label", w["label"]])
    elif w["op"] == "line":
        body = json.loads(run(["api", f"repos/{repo}/issues/{n}", "--jq", "{body: .body}"]))
        lines = (body["body"] or "").split("\n")
        if w["line"] in lines:
            i = len(lines) - 1 - lines[::-1].index(w["line"])
            del lines[i]
            text = "\n".join(lines).rstrip("\n") + "\n"
            run(["api", "--method", "PATCH", f"repos/{repo}/issues/{n}", "-f", f"body={text}"])
    elif w["op"] == "verdict":
        run(["api", "--method", "DELETE", f"repos/{repo}/issues/comments/{w['comment']}"])
    elif w["op"] == "link":
        run(
            [
                "api",
                "--method",
                "DELETE",
                f"repos/{repo}/issues/{n}/dependencies/blocked_by/{w['blocker_id']}",
            ]
        )
    else:
        raise bb.BoardError(f"unknown write {w['op']}")


def compare(docs: dict[str, dict], board: dict) -> list[str]:
    """Where a built board differs from the readback, field by field.

    The fields in ``UNHOMED`` drop out, because they have no home on GitHub on
    purpose. Each section is keyed by its card's issue number, plus the pull
    request number for ``prs``.
    """
    keys = {
        "tracker": lambda x: x["n"],
        "working": lambda x: x["n"],
        "planned": lambda x: x["n"],
        "next": lambda x: x["issue"],
        "prs": lambda x: (x["issue"], x["pr"]),
    }
    out = []
    old_open = docs["state"]["issues"]["open"]
    new_open = board["state"]["issues"]["open"]
    if old_open != new_open:
        out.append(f"state: open issues {old_open} on the artifact, {new_open} built")
    for name, key in keys.items():
        old = {key(x): x for x in docs[name]["items"]}
        new = {key(x): x for x in board[name]["items"]}
        for k in sorted(set(old) | set(new), key=str):
            if k not in new:
                out.append(f"{name} {k}: on the artifact only")
            elif k not in old:
                out.append(f"{name} {k}: built only")
            else:
                skip = UNHOMED[name] | ({"rollup"} if name == "prs" else set())
                fields = (set(old[k]) | set(new[k])) - skip
                for f in sorted(fields):
                    a, b = old[k].get(f), new[k].get(f)
                    if f == "after" and not a and not b:
                        continue
                    if f == "labels":
                        a, b = comparable_labels(a), comparable_labels(b)
                    if a != b:
                        out.append(f"{name} {k} {f}: {a!r} on the artifact, {b!r} built")
    return out


def _log_lines(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "apply"):
        p = sub.add_parser(name)
        p.add_argument("--repo", required=True)
        p.add_argument("--readback", required=True, type=Path)
        if name == "apply":
            p.add_argument("--log", required=True, type=Path)
    u = sub.add_parser("undo")
    u.add_argument("--repo", required=True)
    u.add_argument("--log", required=True, type=Path)
    c = sub.add_parser("compare")
    c.add_argument("--readback", required=True, type=Path)
    c.add_argument("--board", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.cmd == "compare":
            board = json.loads(args.board.read_text(encoding="utf-8"))
            for line in compare(read_readback(args.readback), board):
                print(line)
            return 0
        if args.cmd == "undo":
            # Newest first, and the log is rewritten without each write once it
            # is reversed, so an undo that stops partway can be run again and
            # starts where it stopped rather than failing on a reversed write.
            left = _log_lines(args.log)
            while left:
                w = left[-1]
                undo_write(gh, args.repo, w)
                left.pop()
                args.log.write_text("".join(json.dumps(x) + "\n" for x in left), encoding="utf-8")
                print(f"undone: {json.dumps(w)}")
            return 0
        docs = read_readback(args.readback)
        writes, notes = plan(docs, read_github(bb.GhGraphql(), args.repo))
        for note in notes:
            print(f"note: {note}")
        for w in writes:
            print(f"write: {json.dumps(w)}")
        print(f"{len(writes)} writes, {len(notes)} notes")
        if args.cmd == "apply":
            with args.log.open("a", encoding="utf-8") as log:
                for w in writes:
                    done = apply_write(gh, args.repo, w)
                    log.write(json.dumps(done) + "\n")
                    log.flush()
                    print(f"done: {json.dumps(done)}")
    except bb.BoardError as e:
        print(f"backfill_board: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
