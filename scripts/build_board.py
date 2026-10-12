"""Build the build board's data from GitHub, for the page on GitHub Pages.

The build board is a page answering what is in flight and what to take next.
Until issue 532 every figure on it was measured by hand and written into a
claude.ai artifact's database, which cost session turns on every change and
missed any change no session saw. This script reads every figure from GitHub
and writes them as one ``board.json`` beside the page, and
``.github/workflows/board.yml`` runs it on every change and publishes both on
GitHub Pages. No Claude runs at any step. Issue 532 built it for the figures
GitHub already held. Issue 533 moved the judgement the artifact board held onto
labels, links and marker lines, and retired that board.

It writes the six sections the page reads.

1. ``state``, with the open issue count, the time GitHub was read, and the age
   after which the page calls the board stale.
2. ``tracker``, one card per open issue. Its title, milestone and labels come
   from the issue. ``kind`` comes from labels and sub-issues, ``needs`` from
   native "blocked by" links, and ``after`` from a ``Board after:`` line in the
   body.
3. ``prs``, one item per pull request and issue it names, with its state, its
   checks at the current head, whether GitHub registered the closing link, and
   whether the owner posted a review.
4. ``working``, one item per issue carrying a ``working:build`` or
   ``working:decompose`` label, which a session sets while it holds the card.
5. ``planned``, one item per issue with an owner comment carrying a
   ``Board verdict:`` line, which a decompose loop writes when it exits.
6. ``next``, one item per issue carrying a ``band:N`` label, ordered within its
   band by a ``Board order:`` line in the body.

The ``update-build-board`` skill states each format and when a session sets it.

The page refuses a whole section when one item lacks a field it reads, so
every item carries every such field. A missing milestone is an empty string
rather than a null, and a pull request that names no open issue gets no item
rather than a null issue.

Two labels can disagree, such as two ``band:N`` labels on one issue. The run
takes the lowest band, or ``build`` for both ``working:`` labels, and lists the
conflict in the job summary rather than failing, because one stray label would
otherwise freeze the whole board.

Two of its rules exist because the repository is public.

1. ``reviewed`` reads a comment opening with ``## Review``, and ``planned`` a
   comment carrying a ``Board verdict:`` line, only when its author
   association is ``OWNER``. Anyone can comment, and a stranger's comment would
   otherwise move a card. Labels and links need triage access, so they need no
   such filter.
2. Nothing here reads the event that started the run. Every fact comes from
   the API, so an issue title never reaches a shell, and two runs started by
   different events build the same board from the same state.

It fails closed. A failed call, a GraphQL error, or a count that disagrees
with the pages read on every one of ``LIST_READS`` reads stops the run, and
the last good board stays up. Treating an error as an empty list would publish
a board with no pull requests that reads as correct.

It reads through a few nested GraphQL queries rather than one REST call per
issue. ``GITHUB_TOKEN`` allows 1,000 REST requests an hour per repository, and
a busy hour can start 30 runs, so a call per open issue would run out.
``tests/test_build_board_generator.py`` pins how many requests one run makes.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

SCHEMA = 1

# A `Part of` reference, read the way GitHub reads a closing keyword: anywhere
# in a pull request's body, with `#` and the number right after it, and never
# inside a code span or a fenced code block. Sessions write the phrase
# mid-paragraph, as PR 481 did for issue 482, and a rule that read only a line
# opening with it dropped those without saying so. The one difference from
# GitHub, which reads a keyword in any case, is that the reference has to be
# capitalised, because lowercase prose such as "merged in PR 488, part of 458"
# names another pull request's issue and is not one. The owner ruled on issue
# 559 that a sentence mentioning the phrase in passing counts unless a code
# span holds it, as a closing keyword does. `pr_items` strips the code before
# matching.
PART_OF = re.compile(r"\bPart of #(\d+)\b")

# A review comment opens with a line reading `## Review`, which the
# update-build-board skill states as the convention. "## Reviewer" is not one.
REVIEW = re.compile(r"## Review\b")

# The lines and labels a session sets for the judgement the page draws. Each
# line is anchored at the start of a line, so prose quoting one mid-sentence is
# not one. A verdict reads "Board verdict: build after 5 passes", or "decide"
# for a loop that ended on a question only the owner can answer.
VERDICT = re.compile(
    r"^[ \t]*Board verdict: (build|decide) after (\d+) pass(?:es)?\.?[ \t]*$", re.MULTILINE
)
ORDER = re.compile(r"^[ \t]*Board order: (-?\d+(?:\.\d+)?)[ \t]*$", re.MULTILINE)
AFTER = re.compile(r"^[ \t]*Board after:(.*)$", re.MULTILINE)
BAND = re.compile(r"^band:(\d+)$")
WORKING = {"working:build": "build", "working:decompose": "decompose"}

# A fenced code block, opened by three or more backticks or tildes and closed
# by the same run, or left open to the end of the text. A comment quoting the
# verdict format inside a fence would otherwise read as a verdict.
FENCE = re.compile(
    r"^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?(?:^[ \t]*\1[ \t]*$|\Z)", re.MULTILINE | re.DOTALL
)


def unfenced(text: str) -> str:
    """The text with every fenced code block removed, so no line in one is read."""
    return FENCE.sub("", text)


# A run of backticks, which opens an inline code span, and the blank line that
# ends a paragraph. A span closes only at the next run of exactly as many
# backticks inside the same paragraph, and a run nothing closes is literal
# text. That approximates CommonMark rather than implementing it. Only a blank
# line ends a paragraph here, so a heading or a list item with no blank line
# after it is no boundary, and a backslash-escaped backtick still opens a span.
# In those rare shapes a stray backtick pairs with the wrong partner. A span
# can then run on and swallow a reference, or close early and leave a quoted
# one outside code, so the approximation can drop a reference or credit one.
TICKS = re.compile(r"`+")
PARAGRAPH = re.compile(r"\n[ \t]*\n")


def _spans_out(paragraph: str) -> str:
    """One paragraph with each code span replaced by a space."""
    kept, start, pos = [], 0, 0
    while opener := TICKS.search(paragraph, pos):
        width = len(opener.group())
        closer = next(
            (m for m in TICKS.finditer(paragraph, opener.end()) if len(m.group()) == width), None
        )
        if closer is None:
            pos = opener.end()
            continue
        kept.append(paragraph[start : opener.start()])
        start = pos = closer.end()
    kept.append(paragraph[start:])
    # A space rather than nothing, so the text either side of a span does not
    # join into a phrase GitHub never shows.
    return " ".join(kept)


def outside_code(text: str) -> str:
    """The text with every fenced code block and inline code span removed.

    GitHub does not read a closing keyword written inside either, so a ``Part
    of`` reference written inside one does not count here either.
    """
    # GitHub's web editor saves `\r\n`, which the fence's `$` and the blank
    # line between paragraphs would otherwise never match.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n\n".join(_spans_out(p) for p in PARAGRAPH.split(unfenced(text)))


# Which label sets a card's kind, in the order that wins when an issue carries
# more than one. A parent is read from sub-issues instead, ahead of all three.
KIND_LABELS = (("blocked-on-data", "data"), ("deferred", "deferred"), ("decision", "decision"))

# GitHub reports a check as an uppercase enum, and the page knows four
# lowercase words. Passed through as they come, every state reads as green,
# because the page counted only `failure`, `running` and `neutral`. So each
# state is mapped, and each failure-like one is `failure`. A check run that has
# not completed is `running` whatever its conclusion field says.
CHECK_WORD = {
    # Check run conclusions.
    "SUCCESS": "success",
    "NEUTRAL": "neutral",
    "SKIPPED": "neutral",
    "STALE": "neutral",
    "FAILURE": "failure",
    "TIMED_OUT": "failure",
    "CANCELLED": "failure",
    "ACTION_REQUIRED": "failure",
    "STARTUP_FAILURE": "failure",
    # Status context states. `SUCCESS` and `FAILURE` are shared with the above.
    "ERROR": "failure",
    "PENDING": "running",
    "EXPECTED": "running",
}

PAGE_INFO = "pageInfo{hasNextPage endCursor}"

PR_FIELDS = f"""
fragment pr on PullRequest {{
  id number state body isCrossRepository
  closingIssuesReferences(first:100){{{PAGE_INFO} nodes{{number}}}}
  comments(first:100){{{PAGE_INFO} nodes{{authorAssociation body}}}}
  commits(last:1){{nodes{{commit{{statusCheckRollup{{id
    contexts(first:100){{{PAGE_INFO} nodes{{__typename
      ... on CheckRun{{name status conclusion}}
      ... on StatusContext{{context state}}}}}}}}}}}}}}
}}
"""

ISSUES_QUERY = f"""
query($owner:String!, $name:String!, $after:String) {{
  rateLimit{{cost}}
  repository(owner:$owner, name:$name) {{
    issues(states:OPEN, first:100, after:$after, orderBy:{{field:CREATED_AT, direction:ASC}}) {{
      totalCount {PAGE_INFO}
      nodes {{
        id number title body
        milestone{{title}}
        labels(first:100){{{PAGE_INFO} nodes{{name}}}}
        blockedBy(first:100){{{PAGE_INFO} nodes{{number state repository{{nameWithOwner}}}}}}
        subIssues{{totalCount}}
        issueComments: comments(first:100){{{PAGE_INFO} nodes{{authorAssociation body}}}}
        closedByPullRequestsReferences(first:100, includeClosedPrs:true){{
          {PAGE_INFO} nodes{{number}}}}
        timelineItems(itemTypes:[CROSS_REFERENCED_EVENT], first:100){{{PAGE_INFO} nodes{{
          ... on CrossReferencedEvent{{source{{
            ... on PullRequest{{number repository{{nameWithOwner}}}}}}}}}}}}
      }}
    }}
  }}
}}
"""

OPEN_PRS_QUERY = f"""
query($owner:String!, $name:String!, $after:String) {{
  rateLimit{{cost}}
  repository(owner:$owner, name:$name) {{
    pullRequests(states:OPEN, first:50, after:$after) {{
      totalCount {PAGE_INFO}
      nodes{{...pr}}
    }}
  }}
}}
{PR_FIELDS}
"""

# Pull requests fetched by number, for the merged and closed ones an open issue
# still names. Fifty a query keeps one response small.
BATCH = 50

# How the nested lists that can outgrow one page are read again from where the
# first page stopped. Each is keyed by the name the response carries it under,
# and names the type that holds the list, the field that name stands for, the
# list's arguments and what to select from each entry. An issue's comments and
# a pull request's are both `comments` on GitHub, so the issue's go under an
# alias to keep the two apart.
NESTED = {
    "labels": ("Issue", "labels", "", "name"),
    "blockedBy": ("Issue", "blockedBy", "", "number state repository{nameWithOwner}"),
    "issueComments": ("Issue", "comments", "", "authorAssociation body"),
    "closedByPullRequestsReferences": (
        "Issue",
        "closedByPullRequestsReferences",
        "includeClosedPrs:true",
        "number",
    ),
    "timelineItems": (
        "Issue",
        "timelineItems",
        "itemTypes:[CROSS_REFERENCED_EVENT]",
        "... on CrossReferencedEvent{source{... on PullRequest{number repository{nameWithOwner}}}}",
    ),
    "closingIssuesReferences": ("PullRequest", "closingIssuesReferences", "", "number"),
    "comments": ("PullRequest", "comments", "", "authorAssociation body"),
    "contexts": (
        "StatusCheckRollup",
        "contexts",
        "",
        "__typename ... on CheckRun{name status conclusion} ... on StatusContext{context state}",
    ),
}

Gql = Callable[[str, dict], dict]

# How many reads of one list, each from its first page, it takes for a count that
# disagrees to stop the run. An issue filed or a pull request opened between two
# pages makes one read disagree, and the next read usually finds it unchanged.
# Each read starts at once, because the list need only hold still while one
# read runs.
LIST_READS = 3


class BoardError(RuntimeError):
    """A read that cannot be trusted, which stops the run."""


class GhGraphql:
    """Runs GraphQL through ``gh api graphql`` and counts what it spends.

    Every call is one request. ``cost`` sums the points GitHub charged, read
    from the ``rateLimit`` field each top-level query asks for.
    """

    def __init__(self) -> None:
        self.requests = 0
        self.cost = 0

    def __call__(self, query: str, variables: dict) -> dict:
        args = ["gh", "api", "graphql", "-f", f"query={query}"]
        for key, value in variables.items():
            if value is None:
                continue
            flag = "-F" if isinstance(value, int) else "-f"
            args += [flag, f"{key}={value}"]
        self.requests += 1
        done = subprocess.run(args, capture_output=True, text=True, check=False)
        if done.returncode != 0:
            raise BoardError(f"gh api graphql failed: {done.stderr.strip() or done.stdout}")
        try:
            body = json.loads(done.stdout)
        except json.JSONDecodeError as e:
            raise BoardError(f"gh api graphql returned no JSON: {e}") from e
        if body.get("errors"):
            raise BoardError(f"GraphQL errors: {json.dumps(body['errors'])}")
        data = body.get("data")
        if not isinstance(data, dict):
            raise BoardError("GraphQL returned no data")
        self.cost += int((data.get("rateLimit") or {}).get("cost") or 0)
        return data


def _all_nodes(gql: Gql, node_id: str, field: str, conn: dict) -> list:
    """Every entry of a nested list, reading further pages where there are any."""
    nodes = list(conn["nodes"])
    page = conn["pageInfo"]
    typename, real, args, selection = NESTED[field]
    head = f"{args}, " if args else ""
    while page["hasNextPage"]:
        query = (
            "query($id:ID!, $after:String) { node(id:$id) { ... on "
            f"{typename} {{ {field}: {real}({head}first:100, after:$after) "
            f"{{ {PAGE_INFO} nodes{{ {selection} }} }} }} }} }}"
        )
        data = gql(query, {"id": node_id, "after": page["endCursor"]})
        node = data.get("node")
        if not node or field not in node:
            raise BoardError(f"{typename} {node_id} vanished while reading its {field}")
        conn = node[field]
        nodes += conn["nodes"]
        page = conn["pageInfo"]
    return nodes


def _top_pages(gql: Gql, query: str, owner: str, name: str, field: str) -> list[dict]:
    """Every node of a repository-level list, checked against its total."""
    for attempt in range(1, LIST_READS + 1):
        nodes: list[dict] = []
        after = None
        total = None
        while True:
            data = gql(query, {"owner": owner, "name": name, "after": after})
            conn = data["repository"][field]
            if total is None:
                total = conn["totalCount"]
            nodes += conn["nodes"]
            if not conn["pageInfo"]["hasNextPage"]:
                break
            after = conn["pageInfo"]["endCursor"]
        # A list that changed between pages reads more or fewer entries than its
        # count, and the count is the only sign of it. So the loop reads the whole
        # list again from its first page, and a list that disagrees on every read
        # stops the run. GitHub's pages continue after the last entry read, so a
        # change cannot repeat one, and the check on distinct numbers guards
        # against a page that repeats one anyway.
        if len(nodes) == total and len({n["number"] for n in nodes}) == total:
            return nodes
        if attempt < LIST_READS:
            print(
                f"build_board: read {len(nodes)} {field} against a total of {total}, "
                f"reading the list again (read {attempt + 1} of {LIST_READS})",
                file=sys.stderr,
            )
    raise BoardError(f"read {len(nodes)} {field} against a total of {total} on {LIST_READS} reads")


def card_kinds(labels: list[str], sub_issues: int) -> list[str]:
    """Every kind an issue's sub-issues and labels claim, the winning one first.

    An issue with any sub-issue is a parent, whether or not its children have
    closed, because they carry its work. After that the kind labels follow in
    ``KIND_LABELS`` order. More than one entry is a conflict the run reports.
    """
    kinds = ["parent"] if sub_issues else []
    return kinds + [kind for label, kind in KIND_LABELS if label in labels]


def card_kind(labels: list[str], sub_issues: int) -> str:
    """A card's kind, the first that ``card_kinds`` finds, or ready for none."""
    return (card_kinds(labels, sub_issues) or ["ready"])[0]


def check_word(context: dict, unknown: set[str]) -> str:
    """The page's word for one check run or status context."""
    if context.get("__typename") == "CheckRun":
        if context.get("status") != "COMPLETED":
            return "running"
        state = context.get("conclusion")
    else:
        state = context.get("state")
    word = CHECK_WORD.get(state or "")
    if word is None:
        # A state GitHub adds later is reported neither way rather than as a
        # pass, and the job summary names it so the map can learn it.
        unknown.add(str(state))
        return "neutral"
    return word


def _rollup(gql: Gql, pr: dict, unknown: set[str]) -> list[list[str]]:
    commits = pr["commits"]["nodes"]
    rollup = commits[0]["commit"]["statusCheckRollup"] if commits else None
    if not rollup:
        return []
    contexts = _all_nodes(gql, rollup["id"], "contexts", rollup["contexts"])
    out = []
    for c in contexts:
        label = c.get("name") if c.get("__typename") == "CheckRun" else c.get("context")
        out.append([str(label), check_word(c, unknown)])
    return out


def pr_items(
    gql: Gql,
    pr: dict,
    open_issues: set[int],
    unknown: set[str],
    working: frozenset[int] = frozenset(),
) -> list[dict]:
    """One item per open issue the pull request names, or none at all.

    A pull request names an issue through GitHub's closing link or through a
    ``Part of`` reference anywhere in its body outside a code span or a fenced
    code block. One that names no open issue gets no item, because a branch
    with no card has nowhere to be drawn and a null issue would make the page
    refuse the whole section. One that closes two issues gets two items,
    because the page keys pull requests by issue.

    A pull request opened from a fork gets no item either. Anyone can open one
    on a public repository, and its ``Part of`` reference or closing keyword
    would otherwise draw a branch on the card and take it off the free list.
    Reading the author's association instead would drop Dependabot, which
    GitHub marks ``CONTRIBUTOR``, so the test is where the branch lives.

    ``linked`` is always the opposite of ``partOf`` here, because an issue
    named only by a ``Part of`` reference is the one case with no closing link.
    So the page's warning about a closing link GitHub did not register could
    never fire, and issue 533 removed it. A pull request whose keyword sits in
    a code span names no issue GitHub can see, and gets no item at all.

    ``review`` is the word the card's line prints. With no review posted it
    says one is in progress while a session holds the card, which ``working``
    names, and that none is posted otherwise.
    """
    if pr.get("isCrossRepository"):
        return []
    closing = {
        n["number"]
        for n in _all_nodes(gql, pr["id"], "closingIssuesReferences", pr["closingIssuesReferences"])
    }
    part_of = {int(m) for m in PART_OF.findall(outside_code(pr.get("body") or ""))}
    named = sorted((closing | part_of) & open_issues)
    if not named:
        return []
    comments = _all_nodes(gql, pr["id"], "comments", pr["comments"])
    reviewed = any(
        c.get("authorAssociation") == "OWNER" and REVIEW.match((c.get("body") or "").lstrip())
        for c in comments
    )
    state = {"OPEN": "open", "MERGED": "merged", "CLOSED": "closed"}[pr["state"]]
    rollup = _rollup(gql, pr, unknown)
    items = []
    for issue in named:
        item = {
            "pr": pr["number"],
            "issue": issue,
            "state": state,
            # Never false without `partOf`, so the page no longer reads it, as
            # the docstring says. It is still written for the backfill's
            # `compare` and for anyone reading board.json.
            "linked": issue in closing,
            "reviewed": reviewed,
            "review": "review posted"
            if reviewed
            else ("review in progress" if issue in working else "no review posted"),
            "rollup": rollup,
        }
        if issue not in closing:
            item["partOf"] = True
        items.append(item)
    return items


def _referenced_prs(gql: Gql, issue: dict, repo: str) -> set[int]:
    """The pull requests in this repository that link to or mention an issue."""
    numbers = {
        n["number"]
        for n in _all_nodes(
            gql,
            issue["id"],
            "closedByPullRequestsReferences",
            issue["closedByPullRequestsReferences"],
        )
    }
    for event in _all_nodes(gql, issue["id"], "timelineItems", issue["timelineItems"]):
        source = (event or {}).get("source") or {}
        if "number" in source and source.get("repository", {}).get("nameWithOwner") == repo:
            numbers.add(source["number"])
    return numbers


def _prs_by_number(gql: Gql, owner: str, name: str, numbers: list[int]) -> list[dict]:
    found = []
    for i in range(0, len(numbers), BATCH):
        chunk = numbers[i : i + BATCH]
        fields = " ".join(f"p{n}: pullRequest(number:{n}){{...pr}}" for n in chunk)
        query = (
            "query($owner:String!, $name:String!) { rateLimit{cost} "
            f"repository(owner:$owner, name:$name) {{ {fields} }} }}\n{PR_FIELDS}"
        )
        data = gql(query, {"owner": owner, "name": name})
        for n in chunk:
            pr = data["repository"].get(f"p{n}")
            if pr is None:
                raise BoardError(f"pull request {n} could not be read")
            found.append(pr)
    return found


def tracker_card(
    gql: Gql,
    issue: dict,
    names: list[str],
    open_issues: set[int],
    repo: str,
    conflicts: list[str],
) -> dict:
    """One open issue as the card the page draws.

    A blocker that has closed no longer holds the card, and a number that is
    no open issue has no card to draw, so ``needs`` and ``after`` keep only open
    issues. A "blocked by" link can name an issue in another repository, whose
    number means nothing here, so it is dropped too. ``after`` is left out when
    it names none, as the page reads it as optional. The board's own labels are
    drawn as the rank chip and the busy stripe, so they are left off the card's
    label chips. An issue claiming two kinds takes the first and is reported.
    """
    n = issue["number"]
    blockers = _all_nodes(gql, issue["id"], "blockedBy", issue["blockedBy"])
    kinds = card_kinds(names, issue["subIssues"]["totalCount"])
    if len(kinds) > 1:
        conflicts.append(f"#{n} reads as {' and '.join(kinds)}, read as {kinds[0]}")
    card = {
        "n": n,
        "ms": (issue.get("milestone") or {}).get("title") or "",
        "label": issue["title"],
        "kind": (kinds or ["ready"])[0],
        "needs": sorted(
            {
                b["number"]
                for b in blockers
                if b["state"] == "OPEN" and (b.get("repository") or {}).get("nameWithOwner") == repo
            }
            & open_issues
        ),
        "labels": [x for x in names if not BAND.match(x) and x not in WORKING],
    }
    lines = AFTER.findall(unfenced(issue.get("body") or ""))
    after = {int(m) for line in lines for m in re.findall(r"#(\d+)\b", line)}
    after = sorted((after & open_issues) - {n})
    if after:
        card["after"] = after
    return card


def latest_verdict(comments: list[dict]) -> tuple[str, int] | None:
    """The newest decompose verdict among the owner's comments on an issue.

    A loop run again on the same issue writes a new verdict, so the last one
    wins. GitHub lists comments oldest first.
    """
    found = None
    for c in comments:
        if c.get("authorAssociation") != "OWNER":
            continue
        for ready, passes in VERDICT.findall(unfenced(c.get("body") or "")):
            found = (ready, int(passes))
    return found


def rank_entry(
    n: int,
    names: list[str],
    body: str,
    kind: str,
    verdict: tuple[str, int] | None,
    conflicts: list[str],
) -> dict | None:
    """The card's place in the priority order, or None when it has none.

    ``ready`` has no home of its own. A finished plan says whether it is ready
    to build or waits on the owner, a card whose kind is a decision waits on
    the owner, and any other card still needs a plan.
    """
    bands = sorted(int(m.group(1)) for x in names if (m := BAND.match(x)))
    if not bands:
        return None
    if len(bands) > 1:
        conflicts.append(f"#{n} carries {len(bands)} band labels, read as band:{bands[0]}")
    entry: dict = {
        "issue": n,
        "band": bands[0],
        "ready": verdict[0] if verdict else ("decide" if kind == "decision" else "plan"),
    }
    orders = ORDER.findall(unfenced(body))
    if orders:
        if len(set(orders)) > 1:
            conflicts.append(f"#{n} carries {len(orders)} order lines, read as {orders[0]}")
        value = float(orders[0])
        entry["order"] = int(value) if value.is_integer() else value
    return entry


def stale_after_minutes(workflow: Path) -> int:
    """Twice the longest gap between two scheduled runs, from the workflow.

    The threshold is read from the cron line rather than written beside it,
    because a second copy of the interval drifts the first time the schedule
    changes. Only the forms the workflow uses are understood: a minute list or
    step, with every other field ``*``. Anything else stops the run rather than
    guessing.
    """
    crons = re.findall(r"""^\s*-\s*cron:\s*["']([^"']+)["']""", workflow.read_text(), re.M)
    if len(crons) != 1:
        raise BoardError(f"{workflow} carries {len(crons)} cron lines, expected 1")
    fields = crons[0].split()
    if len(fields) != 5 or any(f != "*" for f in fields[1:]):
        raise BoardError(f"cron {crons[0]!r} is not an hourly minute list")
    minute = fields[0]
    if minute.startswith("*/"):
        minutes = list(range(0, 60, int(minute[2:])))
    else:
        minutes = sorted({int(m) for m in minute.split(",")})
    if not minutes or any(not 0 <= m < 60 for m in minutes):
        raise BoardError(f"cron {crons[0]!r} has no usable minutes")
    gaps = [(b - a) for a, b in zip(minutes, minutes[1:], strict=False)]
    gaps.append(minutes[0] + 60 - minutes[-1])
    return 2 * max(gaps)


def build(gql: Gql, repo: str, stale_after: int, now: datetime) -> tuple[dict, dict]:
    """The board, and what the job summary reports about the read."""
    owner, name = repo.split("/", 1)
    issues = _top_pages(gql, ISSUES_QUERY, owner, name, "issues")
    open_issues = {i["number"] for i in issues}

    tracker = []
    working = []
    planned = []
    ranked = []
    conflicts: list[str] = []
    referenced: set[int] = set()
    for issue in sorted(issues, key=lambda i: i["number"]):
        n = issue["number"]
        names = [lb["name"] for lb in _all_nodes(gql, issue["id"], "labels", issue["labels"])]
        card = tracker_card(gql, issue, names, open_issues, repo, conflicts)
        tracker.append(card)

        held = [WORKING[x] for x in names if x in WORKING]
        if held:
            if len(held) > 1:
                conflicts.append(f"#{n} carries both working labels, read as build")
            working.append({"n": n, "kind": "build" if "build" in held else held[0]})

        comments = _all_nodes(gql, issue["id"], "issueComments", issue["issueComments"])
        verdict = latest_verdict(comments)
        if verdict:
            planned.append({"n": n, "passes": verdict[1], "ready": verdict[0]})

        entry = rank_entry(n, names, issue.get("body") or "", card["kind"], verdict, conflicts)
        if entry:
            ranked.append(entry)

        referenced |= _referenced_prs(gql, issue, repo)

    open_prs = _top_pages(gql, OPEN_PRS_QUERY, owner, name, "pullRequests")
    seen = {p["number"] for p in open_prs}
    others = _prs_by_number(gql, owner, name, sorted(referenced - seen))

    unknown: set[str] = set()
    prs = []
    left_out = []
    busy = frozenset(w["n"] for w in working)
    for pr in open_prs + others:
        items = pr_items(gql, pr, open_issues, unknown, busy)
        if not items and pr["state"] == "OPEN":
            left_out.append(pr["number"])
        prs += items
    prs.sort(key=lambda p: (p["issue"], p["pr"]))

    board = {
        "state": {
            "schema": SCHEMA,
            "updatedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "issues": {"open": len(issues)},
            "source": "github",
            "staleAfterMinutes": stale_after,
        },
        "prs": {"schema": SCHEMA, "items": prs},
        "working": {"schema": SCHEMA, "items": working},
        "planned": {"schema": SCHEMA, "items": planned},
        "next": {"schema": SCHEMA, "items": ranked},
        "tracker": {"schema": SCHEMA, "items": tracker},
    }
    report = {
        "open_issues": len(issues),
        "open_prs": len(open_prs),
        "other_prs_read": len(others),
        "pr_items": len(prs),
        "open_prs_left_out": sorted(left_out),
        "unknown_check_states": sorted(unknown),
        "label_conflicts": conflicts,
    }
    return board, report


def _summary(lines: list[str]) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    text = "\n".join(lines) + "\n"
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


def _output(key: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")


def cmd_build(args: argparse.Namespace) -> None:
    gql = GhGraphql()
    now = datetime.now(UTC)
    board, report = build(gql, args.repo, stale_after_minutes(Path(args.workflow)), now)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "board.json").write_text(
        json.dumps(board, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    updated = board["state"]["updatedAt"]
    _output("updated_at", updated)
    _summary(
        [
            "## Board build",
            "",
            "| Measure | Value |",
            "| --- | --- |",
            f"| GitHub read at | {updated} |",
            f"| GraphQL requests | {gql.requests} |",
            f"| GraphQL points | {gql.cost} |",
            f"| Open issues | {report['open_issues']} |",
            f"| Open pull requests | {report['open_prs']} |",
            f"| Merged or closed pull requests read | {report['other_prs_read']} |",
            f"| Pull request items written | {report['pr_items']} |",
            "| Open pull requests naming no open issue | "
            f"{', '.join(f'#{n}' for n in report['open_prs_left_out']) or 'none'} |",
            "| Check states mapped to neither way | "
            f"{', '.join(report['unknown_check_states']) or 'none'} |",
            f"| Labels or lines that disagree | {'; '.join(report['label_conflicts']) or 'none'} |",
        ]
    )


def _get(url: str) -> tuple[int, dict, bytes]:
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, dict(r.headers), r.read()
    except Exception as e:
        return 0, {"error": str(e)}, b""


def _stamp(body: bytes) -> str | None:
    try:
        return json.loads(body)["state"]["updatedAt"]
    except Exception:
        return None


def cmd_measure(args: argparse.Namespace) -> None:
    """Record how long a run's board takes to reach a reader, and through what.

    Two of the three numbers issue 532 sets out to measure need a deployed
    board, so this runs after every deploy and writes them to the job summary.

    1. The time from the run being created, which is when GitHub queued the
       event, to the new board being served.
    2. Whether a plain fetch gets past Pages' ``cache-control: max-age=600``,
       against a fetch carrying a query string as the page's own does.

    It never fails the run. A measurement that times out says so in the
    summary, and the board it measures is already deployed.
    """
    created = None
    done = subprocess.run(
        ["gh", "api", f"repos/{args.repo}/actions/runs/{args.run_id}", "--jq", ".created_at"],
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode == 0 and done.stdout.strip():
        created = datetime.fromisoformat(done.stdout.strip().replace("Z", "+00:00"))
    base = args.page_url if args.page_url.endswith("/") else args.page_url + "/"
    start = time.monotonic()
    busted_at = None
    while time.monotonic() - start < args.wait:
        _, _, body = _get(f"{base}board.json?t={time.time_ns()}")
        if _stamp(body) == args.updated_at:
            busted_at = datetime.now(UTC)
            break
        time.sleep(5)
    status, headers, body = _get(f"{base}board.json")
    plain_new = _stamp(body) == args.updated_at
    lines = ["## Board delivery", "", "| Measure | Value |", "| --- | --- |"]
    lines.append(f"| Run created | {created.isoformat() if created else 'unknown'} |")
    lines.append(f"| Board built from GitHub at | {args.updated_at} |")
    if busted_at and created:
        secs = round((busted_at - created).total_seconds())
        lines.append(f"| Created to served, with a query string | {secs} s |")
    else:
        lines.append(
            f"| Created to served, with a query string | not served within {args.wait} s |"
        )
    lines.append(f"| Plain fetch served the new board | {'yes' if plain_new else 'no'} |")
    for key in ("cache-control", "age", "x-cache", "x-served-by"):
        value = next((v for k, v in headers.items() if k.lower() == key), "")
        lines.append(f"| Plain fetch `{key}` | {value or 'absent'} |")
    lines.append(f"| Plain fetch status | {status} |")
    _summary(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="read GitHub and write board.json")
    b.add_argument("--repo", required=True)
    b.add_argument("--workflow", required=True)
    b.add_argument("--out", required=True)
    b.set_defaults(func=cmd_build)
    m = sub.add_parser("measure", help="time how long a deployed board takes to be served")
    m.add_argument("--repo", required=True)
    m.add_argument("--run-id", required=True)
    m.add_argument("--page-url", required=True)
    m.add_argument("--updated-at", required=True)
    m.add_argument("--wait", type=int, default=60)
    m.set_defaults(func=cmd_measure)
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except BoardError as e:
        print(f"build_board: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
