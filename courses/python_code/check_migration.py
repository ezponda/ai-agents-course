#!/usr/bin/env python3
"""Acceptance checks for the portable-markup migration, reported as numbers.

Every check compares the working tree against a git ref, or the built HTML
against a build of that ref. Each one prints its counts so the result can be
read rather than trusted.

Usage::

    python3 check_migration.py --ref 3201ca3 \\
        --before <html-of-ref-build> --after <html-of-current-build>
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys
from pathlib import Path

BOOK = Path(__file__).resolve().parent / "book"
KINDS = ("note", "tip", "warning", "important")


def joined(source) -> str:
    return source if isinstance(source, str) else "".join(source)


def at_ref(path: Path, ref: str) -> dict:
    rel = f"courses/python_code/book/{path.name}"
    out = subprocess.run(
        ["git", "show", f"{ref}:{rel}"], capture_output=True, text=True, cwd=BOOK
    )
    return json.loads(out.stdout)


def article_text(page: Path) -> str:
    import html as H

    raw = page.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"<article.*?</article>", raw, re.S)
    text = match.group(0) if match else raw
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", text, flags=re.S)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", text))).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ref", default="3201ca3")
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    args = parser.parse_args()

    notebooks = sorted(BOOK.glob("*.ipynb"))
    failures: list[str] = []

    # ---- A: no code cell changed ------------------------------------
    code_cells = code_changed = 0
    # ---- B: prose, links, code blocks and table rows unchanged -------
    prose_changed = links_changed = fences_changed = rows_changed = 0
    # ---- C: structure identical -------------------------------------
    struct_problems = 0
    # ---- F: no MyST left --------------------------------------------
    myst_left = 0
    # ---- G: launch note --------------------------------------------
    note_missing = note_stale = note_no_colab = note_no_lab = note_wrong_target = 0

    myst_re = re.compile(r"^:{3,}|^`{3,}\{(note|tip|warning|important|dropdown)\}|^:color:", re.M)
    strip_re = [
        (re.compile(r"^:{3,}\{dropdown\}.*$", re.M), ""),
        (re.compile(r"^:color:.*$", re.M), ""),
        (re.compile(r"^:{3,}$", re.M), ""),
        (re.compile(r"^`{3,}\{(note|tip|warning|important)\}$", re.M), ""),
        (re.compile(r"^`{3,}$", re.M), ""),
        (re.compile(r"</?details[^>]*>|</?summary>|</?blockquote[^>]*>", 0), ""),
        (re.compile(r'<p class="admonition-title">.*?</p>'), ""),
        (re.compile(r"^.*\*\*Run it:\*\*.*$", re.M), ""),
        (re.compile(r"<code>|</code>|<strong>|</strong>"), "`"),
    ]

    def normalise(text: str) -> str:
        for pattern, repl in strip_re:
            text = pattern.sub(repl, text)
        return re.sub(r"\s+", " ", text).strip()

    for path in notebooks:
        old, new = at_ref(path, args.ref), json.loads(path.read_text(encoding="utf-8"))
        oc, nc = old["cells"], new["cells"]
        if len(oc) != len(nc):
            struct_problems += 1
            failures.append(f"C {path.name}: cell count {len(oc)} -> {len(nc)}")
            continue
        if old.get("metadata", {}).get("kernelspec") != new.get("metadata", {}).get("kernelspec"):
            struct_problems += 1
            failures.append(f"C {path.name}: kernelspec changed")
        if old.get("metadata", {}).get("language_info") != new.get("metadata", {}).get("language_info"):
            struct_problems += 1
            failures.append(f"C {path.name}: language_info changed")

        for i, (a, b) in enumerate(zip(oc, nc)):
            if a["cell_type"] != b["cell_type"]:
                struct_problems += 1
                failures.append(f"C {path.name} cell {i}: type changed")
                continue
            if a.get("outputs") != b.get("outputs"):
                struct_problems += 1
                failures.append(f"C {path.name} cell {i}: outputs changed")
            if a.get("id") != b.get("id"):
                struct_problems += 1
                failures.append(f"C {path.name} cell {i}: id changed")
            sa, sb = joined(a["source"]), joined(b["source"])
            if a["cell_type"] == "code":
                code_cells += 1
                if sa != sb:
                    code_changed += 1
                    failures.append(f"A {path.name} cell {i}: code cell modified")
                continue
            if normalise(sa) != normalise(sb):
                prose_changed += 1
                failures.append(f"B {path.name} cell {i}: prose changed")
            la = sorted(re.findall(r"\]\(([^)]+)\)", sa))
            lb = sorted(re.findall(r"\]\(([^)]+)\)", sb))
            if la != lb:
                links_changed += 1
                failures.append(f"B {path.name} cell {i}: links changed")
            fa = re.findall(r"```[a-z]*\n(.*?)```", sa, re.S)
            fb = re.findall(r"```[a-z]*\n(.*?)```", sb, re.S)
            if fa != fb:
                fences_changed += 1
                failures.append(f"B {path.name} cell {i}: fenced code changed")
            ra = len(re.findall(r"^\s*\|.+\|\s*$", sa, re.M))
            rb = len(re.findall(r"^\s*\|.+\|\s*$", sb, re.M))
            if ra != rb:
                rows_changed += 1
                failures.append(f"B {path.name} cell {i}: table rows {ra} -> {rb}")

        whole_new = "\n".join(joined(c["source"]) for c in nc)
        whole_old = "\n".join(joined(c["source"]) for c in oc)
        found = myst_re.findall(whole_new)
        if found:
            myst_left += len(found)
            failures.append(f"F {path.name}: {len(found)} MyST fragment(s) left")

        if "**Run it:**" in whole_old:
            line = re.search(r"^.*\*\*Run it:\*\*.*$", whole_new, re.M)
            if line is None:
                note_missing += 1
                failures.append(f"G {path.name}: launch note missing")
            else:
                text = line.group(0)
                if "full MyST rendering" in text or "simplified formatting" in text:
                    note_stale += 1
                    failures.append(f"G {path.name}: launch note still stale")
                if "local_setup.md" not in text:
                    note_no_lab += 1
                    failures.append(f"G {path.name}: launch note lost local_setup link")
                colab = re.search(r"colab\.research\.google\.com[^)]*/([\w.]+\.ipynb)", text)
                if colab is None:
                    note_no_colab += 1
                    failures.append(f"G {path.name}: launch note lost Colab link")
                elif colab.group(1) != path.name:
                    note_wrong_target += 1
                    failures.append(f"G {path.name}: Colab link points at {colab.group(1)}")

    # ---- D / E: counts in the built HTML ----------------------------
    def admonitions(root: Path) -> collections.Counter:
        counts: collections.Counter = collections.Counter()
        for page in root.glob("*.html"):
            for classes in re.findall(r'class="[^"]*\badmonition\b[^"]*"', page.read_text(errors="replace")):
                for kind in KINDS:
                    if re.search(rf"\b{kind}\b", classes):
                        counts[kind] += 1
        return counts

    before_adm, after_adm = admonitions(args.before), admonitions(args.after)

    details = opened = summaries = 0
    for page in args.after.glob("*.html"):
        raw = page.read_text(errors="replace")
        details += len(re.findall(r"<details\b", raw))
        opened += len(re.findall(r"<details[^>]*\bopen\b", raw))
        summaries += len(re.findall(r"<summary\b", raw))
    ref_dropdowns = sum(
        len(re.findall(r"^:{3,}\{dropdown\}", joined(c["source"]), re.M))
        for p in notebooks for c in at_ref(p, args.ref)["cells"]
        if c["cell_type"] == "markdown"
    )

    # non-converted pages must be byte-equal in text
    unchanged_diff = 0
    for page in sorted(args.before.glob("*.html")):
        twin = args.after / page.name
        if twin.exists() and article_text(page) != article_text(twin):
            unchanged_diff += 1

    print(f"Notebooks: {len(notebooks)}\n")
    print(f"A  code cells compared . . . . . . {code_cells:5}   modified: {code_changed}")
    print(f"B  prose / links / fences / rows .        changed: {prose_changed} / {links_changed} / {fences_changed} / {rows_changed}")
    print(f"C  structure problems . . . . . . {struct_problems:5}   (cells, types, outputs, ids, kernelspec, language_info)")
    print(f"D  .admonition before . . . . . . {dict(sorted(before_adm.items()))}  total {sum(before_adm.values())}")
    print(f"   .admonition after  . . . . . . {dict(sorted(after_adm.items()))}  total {sum(after_adm.values())}")
    print(f"E  {{dropdown}} at {args.ref[:7]} . . . . . {ref_dropdowns:5}")
    print(f"   <details> built  . . . . . . . {details:5}   <summary>: {summaries}   open by default: {opened}")
    print(f"F  MyST fragments left . . . . . {myst_left:5}")
    print(f"G  launch note: missing {note_missing}, stale {note_stale}, no Colab {note_no_colab}, no local_setup {note_no_lab}, wrong target {note_wrong_target}")
    print(f"   pages whose rendered text differs from the {args.ref[:7]} build: {unchanged_diff}")

    if before_adm != after_adm:
        failures.append(f"D admonition counts differ: {dict(before_adm)} -> {dict(after_adm)}")
    if details != ref_dropdowns:
        failures.append(f"E {ref_dropdowns} dropdowns at ref but {details} <details> built")
    if summaries != details:
        failures.append(f"E {details} <details> but {summaries} <summary>")
    if opened:
        failures.append(f"E {opened} <details> open by default")

    if failures:
        print(f"\n{len(failures)} failure(s):", file=sys.stderr)
        for failure in failures[:40]:
            print(f"  {failure}", file=sys.stderr)
        sys.exit(1)
    print("\nPASSED: A-G all clean.")


if __name__ == "__main__":
    main()
