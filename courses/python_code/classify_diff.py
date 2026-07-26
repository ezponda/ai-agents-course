#!/usr/bin/env python3
"""Classify every changed line of a notebook diff into an expected shape.

The migration is only allowed to change markup. This reads ``git diff`` for the
notebooks in a revision range and assigns each added or removed line to one of
the shapes the conversion produces. Anything it cannot classify is reported and
makes the run fail, so an unexpected edit cannot ride along unnoticed.

Usage::

    python3 classify_diff.py HEAD~1 HEAD
    python3 classify_diff.py HEAD~1 HEAD --files book/02_*.ipynb
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys

# Diff lines are JSON strings inside the .ipynb, e.g.  +    "</details>"
SHAPES: list[tuple[str, re.Pattern]] = [
    ("<details> open", re.compile(r'^<details class="course-dropdown[^"]*">$')),
    ("</details> close", re.compile(r"^</details>$")),
    ("<summary>", re.compile(r"^<summary>.*</summary>$")),
    ("<blockquote admonition> open", re.compile(r'^<blockquote class="admonition \w+">$')),
    ("</blockquote> close", re.compile(r"^</blockquote>$")),
    ("<p admonition-title>", re.compile(r'^<p class="admonition-title">.*</p>$')),
    ("required blank line", re.compile(r"^$")),
    ("MyST dropdown open", re.compile(r"^:{3,}\{dropdown\}")),
    ("MyST fence close", re.compile(r"^:{3,}$|^`{3,}$")),
    ("MyST admonition open", re.compile(r"^`{3,}\{(note|tip|warning|important)\}")),
    ("MyST :color: option", re.compile(r"^:color:")),
    ('"Run it" note', re.compile(r"^>\s*\*\*Run it:\*\*")),
]


def payload(diff_line: str) -> str | None:
    """The cell text a diff line carries, or None if it is not a source line.

    Notebook source lines are JSON strings; everything else in the diff is
    structural (braces, keys, the "source" key itself).
    """
    body = diff_line[1:].strip()
    if body.endswith(","):
        body = body[:-1]
    if not (body.startswith('"') and body.endswith('"')):
        return None
    try:
        return json.loads(body).rstrip("\n")
    except json.JSONDecodeError:
        return None


def classify(text: str) -> str | None:
    for name, pattern in SHAPES:
        if pattern.match(text):
            return name
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("base")
    parser.add_argument("head", help='revision, or "WORKTREE" for uncommitted changes')
    parser.add_argument("--files", nargs="*", default=["*.ipynb"])
    args = parser.parse_args()

    rev = [args.base] if args.head == "WORKTREE" else [f"{args.base}..{args.head}"]
    diff = subprocess.run(
        ["git", "diff", *rev, "--", *args.files], capture_output=True, text=True
    ).stdout

    counts: collections.Counter[str] = collections.Counter()
    unknown: list[str] = []
    structural = 0

    for line in diff.splitlines():
        if not line or line[0] not in "+-" or line[:3] in ("+++", "---"):
            continue
        text = payload(line)
        if text is None:
            structural += 1
            continue
        shape = classify(text)
        if shape is None:
            unknown.append(f"{line[0]} {text[:110]}")
        else:
            counts[shape] += 1

    total = sum(counts.values())
    print(f"Classified {total} source lines ({structural} structural JSON lines ignored).\n")
    for shape, count in counts.most_common():
        print(f"  {count:5}  {shape}")

    if unknown:
        print(f"\n{len(unknown)} UNEXPECTED line shape(s):", file=sys.stderr)
        for line in unknown[:25]:
            print(f"  {line}", file=sys.stderr)
        sys.exit(1)
    print("\nPASSED: every changed line matches an expected shape.")


if __name__ == "__main__":
    main()
