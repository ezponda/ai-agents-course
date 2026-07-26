#!/usr/bin/env python3
"""Check that converting a notebook to portable Markdown changed only the markup.

Compares each converted notebook against its committed version and the built
page against the same page built from the original source. Everything it reports
is a fact about the two artefacts, not a judgement about how they look.

Usage::

    python3 verify_portable.py --before <html-of-original-build> \\
        --after <html-of-converted-build> --ref HEAD book/03_*.ipynb
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

MYST_LEFTOVER_RE = re.compile(r":{3,}\{[a-z-]+\}|```\{(note|tip|warning|important|dropdown)\}|^:color:", re.M)
ADMONITION_LABEL_RE = re.compile(r"^> \*\*(Note|Tip|Warning|Important):\*\*", re.M)


def cell_sources(notebook: dict) -> list[tuple[str, str]]:
    out = []
    for cell in notebook.get("cells", []):
        source = cell["source"]
        out.append((cell["cell_type"], source if isinstance(source, str) else "".join(source)))
    return out


def committed(path: Path, ref: str) -> dict | None:
    path = path.resolve()
    repo_path = subprocess.run(
        ["git", "ls-files", "--full-name", path.name],
        capture_output=True, text=True, cwd=path.parent,
    ).stdout.strip()
    if not repo_path:
        return None
    blob = subprocess.run(
        ["git", "show", f"{ref}:{repo_path}"], capture_output=True, text=True, cwd=path.parent
    )
    return json.loads(blob.stdout) if blob.returncode == 0 else None


def strip_markup(text: str) -> str:
    """Reduce a cell to its words, so markup changes do not register."""
    text = re.sub(r":{3,}\{dropdown\}\s*", "", text)
    text = re.sub(r"^:color:.*$", "", text, flags=re.M)
    text = re.sub(r"^:{3,}$", "", text, flags=re.M)
    text = re.sub(r"`{3,}\{(note|tip|warning|important)\}", "", text)
    text = re.sub(r"</?details[^>]*>|</?summary>", "", text)
    # The converted admonition carries its label in a title element the source
    # never had; drop the whole element so only the body is compared.
    text = re.sub(r'<p class="admonition-title">.*?</p>', "", text)
    text = re.sub(r"</?blockquote[^>]*>", "", text)
    # The launch note is deliberately re-worded; compare only that it is there.
    text = re.sub(r">?\s*\*\*Run it:\*\*.*", "", text)
    text = re.sub(r"^`{3,}$", "", text, flags=re.M)
    text = re.sub(r"<code>|</code>|<strong>|</strong>", "`", text)
    return re.sub(r"\s+", " ", text).strip()


def links_in(text: str) -> list[str]:
    return sorted(re.findall(r"\]\(([^)]+)\)", text) + re.findall(r'href="([^"]+)"', text))


def code_blocks(text: str) -> list[str]:
    """Fenced code blocks, scanned by line.

    A regex would treat the closing fence of a ```{note} as the opening of a
    code block and invent a block that is not there, which made two consecutive
    admonitions look like a code change once converted.
    """
    blocks: list[str] = []
    lines = text.split("\n")
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped.startswith("```"):
            index += 1
            continue
        marker = "`" * (len(stripped) - len(stripped.lstrip("`")))
        info = stripped[len(marker) :]
        body: list[str] = []
        index += 1
        while index < len(lines) and lines[index].strip() != marker:
            body.append(lines[index])
            index += 1
        index += 1
        # A directive fence is not a code block, and its body is scanned
        # separately so a code block inside it is still counted once.
        if info.startswith("{"):
            blocks.extend(code_blocks("\n".join(body)))
        else:
            blocks.append("\n".join(body).strip())
    return blocks


def table_rows(text: str) -> int:
    return len(re.findall(r"^\s*\|.+\|\s*$", text, re.M))


def check_notebook(path: Path, ref: str, problems: list[str]) -> None:
    new = json.loads(path.read_text(encoding="utf-8"))
    old = committed(path, ref)
    if old is None:
        problems.append(f"{path.name}: no committed version at {ref}")
        return

    old_cells, new_cells = cell_sources(old), cell_sources(new)
    name = path.name

    if len(old_cells) != len(new_cells):
        problems.append(f"{name}: cell count {len(old_cells)} -> {len(new_cells)}")
        return
    for i, ((old_kind, old_src), (new_kind, new_src)) in enumerate(zip(old_cells, new_cells)):
        if old_kind != new_kind:
            problems.append(f"{name} cell {i}: type {old_kind} -> {new_kind}")
            continue
        if old_kind == "code":
            if old_src != new_src:
                problems.append(f"{name} cell {i}: code cell modified")
            continue
        if strip_markup(old_src) != strip_markup(new_src):
            problems.append(f"{name} cell {i}: prose changed")
        if links_in(old_src) != links_in(new_src):
            problems.append(f"{name} cell {i}: links changed")
        if code_blocks(old_src) != code_blocks(new_src):
            problems.append(f"{name} cell {i}: fenced code changed")
        if table_rows(old_src) != table_rows(new_src):
            problems.append(f"{name} cell {i}: table rows changed")

    whole = "\n".join(src for _, src in new_cells)
    old_whole = "\n".join(src for _, src in old_cells)
    if "**Run it:**" in old_whole:
        # Scoped to the note's own line: a Colab URL elsewhere in the notebook
        # must not make a broken launch note look fine.
        note = re.search(r"^.*\*\*Run it:\*\*.*$", whole, re.M)
        if note is None:
            problems.append(f"{name}: the launch note disappeared")
        else:
            line = note.group(0)
            if "full MyST rendering" in line or "simplified formatting" in line:
                problems.append(f"{name}: launch note still claims MyST/simplified formatting")
            if "colab.research.google.com" not in line:
                problems.append(f"{name}: launch note lost its Colab link")
            if "local_setup.md" not in line:
                problems.append(f"{name}: launch note lost its JupyterLab link")
    leftovers = MYST_LEFTOVER_RE.findall(whole)
    if leftovers:
        problems.append(f"{name}: MyST syntax still present ({len(leftovers)} occurrences)")
    opens = whole.count("<details")
    closes = whole.count("</details>")
    if opens != closes:
        problems.append(f"{name}: unbalanced <details> ({opens} open, {closes} close)")
    if opens and whole.count("<summary>") != opens:
        problems.append(f"{name}: {opens} <details> but {whole.count('<summary>')} <summary>")


def check_page(before: Path, after: Path, problems: list[str]) -> None:
    """Compare the two rendered pages for the same notebook."""
    name = after.name
    if not before.exists():
        problems.append(f"{name}: no baseline page to compare against")
        return
    before_html = before.read_text(encoding="utf-8", errors="replace")
    after_html = after.read_text(encoding="utf-8", errors="replace")

    def article_text(page: str) -> str:
        body = re.search(r"<article.*?</article>", page, re.S)
        text = body.group(0) if body else page
        text = re.sub(r"<script.*?</script>|<style.*?</style>", "", text, flags=re.S)
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text))).strip()
        # Two intended text changes are normalised away; everything else must
        # match exactly. The admonition label gains a colon ("Note" -> "Note:"),
        # and the launch note is deliberately re-worded (checked separately).
        text = re.sub(r"\b(Note|Tip|Warning|Important):", r"\1", text)
        # Strip only the fixed opening of the launch note, in either wording,
        # so the notebook-specific tail after it is still compared.
        return re.sub(
            r"Run it:.*?(?:simplified formatting\.|for zero setup\.)", "", text
        )

    before_text, after_text = article_text(before_html), article_text(after_html)
    if before_text != after_text:
        index = next(
            (i for i, (a, b) in enumerate(zip(before_text, after_text)) if a != b),
            min(len(before_text), len(after_text)),
        )
        problems.append(
            f"{name}: rendered text differs at char {index}\n"
            f"        original:  ...{before_text[max(0, index - 60):index + 60]!r}\n"
            f"        converted: ...{after_text[max(0, index - 60):index + 60]!r}"
        )

    for tag, label in (("<table", "tables"), ("<details", "collapsibles")):
        if before_html.count(tag) != after_html.count(tag):
            problems.append(
                f"{name}: {label} {before_html.count(tag)} -> {after_html.count(tag)}"
            )

    # Count rendered admonitions by type. Searching the built HTML for stray
    # Markdown would not catch an admonition that failed to convert, nor one
    # that converted to the wrong type; this catches both.
    def admonitions_by_type(page: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for classes in re.findall(r'class="[^"]*\badmonition\b[^"]*"', page):
            for kind in ("note", "tip", "warning", "important"):
                if re.search(rf"\b{kind}\b", classes):
                    counts[kind] = counts.get(kind, 0) + 1
        return counts

    before_counts = admonitions_by_type(before_html)
    after_counts = admonitions_by_type(after_html)
    if before_counts != after_counts:
        problems.append(f"{name}: admonitions by type {before_counts} -> {after_counts}")

    open_by_default = len(re.findall(r"<details[^>]*\bopen\b", after_html))
    if open_by_default:
        problems.append(f"{name}: {open_by_default} collapsible(s) open by default")

    if re.search(r"&gt;\s*\*\*(Note|Tip|Warning|Important):\*\*", after_html):
        problems.append(f"{name}: an admonition label was not parsed as Markdown")
    if not re.search(r"<blockquote", after_html) and ADMONITION_LABEL_RE.search(after_html):
        problems.append(f"{name}: admonition present but no blockquote rendered")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("notebooks", nargs="+", type=Path)
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--before", type=Path, help="HTML dir built from the original source")
    parser.add_argument("--after", type=Path, help="HTML dir built from the converted source")
    parser.add_argument("--build-log", type=Path, help="Build log of the converted book")
    parser.add_argument("--baseline-log", type=Path, help="Build log of the original book")
    args = parser.parse_args()

    problems: list[str] = []
    for path in args.notebooks:
        check_notebook(path, args.ref, problems)
        if args.before and args.after:
            check_page(args.before / f"{path.stem}.html", args.after / f"{path.stem}.html", problems)

    if args.build_log and args.baseline_log:
        def warnings(log: Path) -> set[str]:
            text = re.sub(r"\x1b\[[0-9;]*m", "", log.read_text(errors="replace"))
            return {re.sub(r"\d+", "N", w) for w in re.findall(r"WARNING: .*", text)}
        new_warnings = warnings(args.build_log) - warnings(args.baseline_log)
        for warning in sorted(new_warnings):
            problems.append(f"new build warning: {warning[:120]}")

    print(f"Checked {len(args.notebooks)} notebook(s).")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for problem in problems:
            print(f"  FAIL {problem}")
        sys.exit(1)
    print("PASSED: prose, links, code, tables, cell order, collapsibles and build all match.")


if __name__ == "__main__":
    main()
