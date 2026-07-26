#!/usr/bin/env python3
"""Store every notebook cell's ``source`` as a list of lines.

A cell's source may be a single string or a list of lines; both are valid
``.ipynb`` v4 and both render identically. The course currently mixes the two,
sometimes inside one notebook. That makes diffs unreadable: a tool that rewrites
a string cell into a list cell shows up as the whole cell deleted and re-added,
so a one-line change is indistinguishable from a rewrite.

Normalising first, as its own step, means later diffs show only what actually
changed.

The transformation must be invisible: for every cell, ``"".join(source)`` has to
be byte-identical before and after. That is checked here, per cell, and any
mismatch aborts without writing.

Usage::

    python3 normalize_sources.py --check book/*.ipynb    # report only
    python3 normalize_sources.py book/*.ipynb
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def joined(source) -> str:
    return source if isinstance(source, str) else "".join(source)


def normalize(path: Path, write: bool) -> tuple[int, int, list[str]]:
    """Return (cells converted, cells already list, per-cell errors)."""
    notebook = json.loads(path.read_text(encoding="utf-8"))
    converted = already = 0
    errors: list[str] = []

    for number, cell in enumerate(notebook.get("cells", [])):
        source = cell.get("source")
        if source is None:
            continue
        before = joined(source)
        if isinstance(source, list):
            already += 1
            continue

        lines = source.splitlines(keepends=True)
        if "".join(lines) != before:
            errors.append(f"{path.name} cell {number}: text would change")
            continue
        cell["source"] = lines
        converted += 1

    if errors:
        return converted, already, errors

    if write and converted:
        path.write_text(
            json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return converted, already, errors


def check_roundtrip(path: Path, original: dict) -> list[str]:
    """Re-read the written file and compare every cell against the original."""
    written = json.loads(path.read_text(encoding="utf-8"))
    problems = []
    old_cells, new_cells = original.get("cells", []), written.get("cells", [])
    if len(old_cells) != len(new_cells):
        return [f"{path.name}: cell count changed {len(old_cells)} -> {len(new_cells)}"]
    for number, (old, new) in enumerate(zip(old_cells, new_cells)):
        if joined(old.get("source", "")) != joined(new.get("source", "")):
            problems.append(f"{path.name} cell {number}: source text changed")
        if not isinstance(new.get("source"), list):
            problems.append(f"{path.name} cell {number}: source is still not a list")
        if old.get("cell_type") != new.get("cell_type"):
            problems.append(f"{path.name} cell {number}: cell type changed")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("notebooks", nargs="+", type=Path)
    parser.add_argument("--check", action="store_true", help="Report, write nothing.")
    args = parser.parse_args()

    problems: list[str] = []
    total_converted = total_already = touched = 0

    for path in args.notebooks:
        original = json.loads(path.read_text(encoding="utf-8"))
        converted, already, errors = normalize(path, write=not args.check)
        problems.extend(errors)
        total_converted += converted
        total_already += already
        if converted:
            touched += 1
            verb = "would convert" if args.check else "converted"
            print(f"  {path.name}: {verb} {converted} cells ({already} already lists)")
        if converted and not args.check and not errors:
            problems.extend(check_roundtrip(path, original))

    print(
        f"\n{touched} notebook(s) changed. "
        f"{total_converted} cells converted, {total_already} already lists."
    )
    if problems:
        print(f"\n{len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  FAIL {problem}", file=sys.stderr)
        sys.exit(1)
    print("PASSED: every cell's joined source is byte-identical.")


if __name__ == "__main__":
    main()
