#!/usr/bin/env python3
"""Rewrite MyST directives in course notebooks as portable Markdown/HTML.

The book renders `{dropdown}` as ``<details>`` and `{note}` as a styled
``<div>``; that styling comes from CSS, not from the directive. Writing those
elements directly in the source keeps the book looking the same while making the
notebooks render correctly in Colab, GitHub, VS Code and plain JupyterLab.

Two transformations:

``::::{dropdown} Title`` + ``:color: c``  ->  ``<details class="course-dropdown
course-dropdown-c"><summary>Title</summary>``. A blank line after ``<summary>``
is required: without it CommonMark treats the whole block as raw HTML and the
Markdown inside is not parsed.

```` ```{note} ````  ->  ``<blockquote class="admonition note">`` carrying the
theme's own classes, so the book keeps the colour, bar, title band and icon with
no extra CSS. A blockquote survives every renderer, which a ``<div>`` does not:
Colab strips the attributes while sanitising, and a div would then be left with
no visual signal at all whereas a blockquote still reads as a callout.

It also re-words the "Run it" launch note, which claims JupyterLab is needed for
MyST rendering and that Colab is a degraded view. Neither is true afterwards.

Operates on the notebook JSON, cell by cell. Unbalanced directives are a hard
error, not a silent partial conversion.

Usage::

    python3 portable_convert.py book/03_tool_use_from_scratch.ipynb
    python3 portable_convert.py --check book/*.ipynb      # report only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ADMONITION_LABELS = {
    "note": "Note",
    "tip": "Tip",
    "warning": "Warning",
    "important": "Important",
}

# MULTILINE so the same pattern works line-by-line and as a whole-cell probe.
DIRECTIVE_OPEN_RE = re.compile(r"^(:{3,})\{([a-z-]+)\}[ \t]*(.*)$", re.MULTILINE)
ADMONITION_OPEN_RE = re.compile(r"^(`{3,})\{([a-z-]+)\}[ \t]*(.*)$", re.MULTILINE)
OPTION_RE = re.compile(r"^:([a-z-]+):[ \t]*(.*)$")


class ConversionError(Exception):
    """A directive the converter refuses to guess about."""


def inline_to_html(text: str) -> str:
    """Convert the inline Markdown a <summary> may hold.

    Markdown is not parsed inside an HTML open tag, so the few titles that use
    backticks or bold need explicit tags.
    """
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text.strip()


def find_close(lines: list[str], start: int, marker: str) -> int:
    """Index of the line closing a fence opened at ``start``.

    Only a line consisting of exactly the opening marker closes it, so nested
    fences of a different length are left alone.
    """
    for index in range(start + 1, len(lines)):
        if lines[index].strip() == marker:
            return index
    return -1


def convert_admonitions(source: str, where: str) -> str:
    """```{note} ... ``` -> blockquote with an explicit label."""
    lines = source.split("\n")
    out: list[str] = []
    index = 0
    while index < len(lines):
        match = ADMONITION_OPEN_RE.match(lines[index])
        if not match or match.group(2) not in ADMONITION_LABELS:
            out.append(lines[index])
            index += 1
            continue

        marker, kind, argument = match.groups()
        close = find_close(lines, index, marker)
        if close == -1:
            raise ConversionError(f"{where}: unclosed ```{{{kind}}} — no matching {marker}")

        # A body fence of the same length would have closed the directive here.
        # MyST tolerates it; a line-based matcher cannot tell the two apart, so
        # refuse rather than silently truncate the admonition.
        for line in lines[index + 1 : close]:
            if re.match(r"^`{3,}", line.strip()):
                raise ConversionError(
                    f"{where}: ```{{{kind}}} contains a code fence of the same length "
                    f"({marker}). Re-open the directive with one more backtick, or "
                    f"convert this cell by hand."
                )

        body = lines[index + 1 : close]
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()

        label = ADMONITION_LABELS[kind]
        title = f"{label}: {argument.strip()}" if argument.strip() else label
        # A blockquote carrying the theme's own admonition classes. The theme
        # styles .admonition on any element (there is no div.admonition-only
        # selector), so this gets the colour, bar, title band and icon with no
        # extra CSS. Colab drops the attributes and renders a plain blockquote,
        # which still reads as a callout.
        out.append(f'<blockquote class="admonition {kind}">')
        out.append(f'<p class="admonition-title">{title}</p>')
        out.append("")
        out.extend(body)
        out.append("")
        out.append("</blockquote>")
        index = close + 1
    return "\n".join(out)


def convert_dropdowns(source: str, where: str) -> str:
    """::::{dropdown} Title + :color: -> <details>."""
    lines = source.split("\n")
    out: list[str] = []
    index = 0
    while index < len(lines):
        match = DIRECTIVE_OPEN_RE.match(lines[index])
        if not match:
            out.append(lines[index])
            index += 1
            continue

        marker, kind, title = match.groups()
        if kind != "dropdown":
            raise ConversionError(f"{where}: unhandled directive {{{kind}}}")

        close = find_close(lines, index, marker)
        if close == -1:
            raise ConversionError(
                f"{where}: unclosed {marker}{{dropdown}} '{title.strip()[:40]}' — "
                f"no matching {marker}. Fix the source before converting."
            )

        body = lines[index + 1 : close]
        color = "info"
        while body:
            option = OPTION_RE.match(body[0])
            if not option:
                break
            if option.group(1) == "color":
                color = option.group(2).strip() or "info"
            body.pop(0)
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()

        out.append(f'<details class="course-dropdown course-dropdown-{color}">')
        out.append(f"<summary>{inline_to_html(title)}</summary>")
        out.append("")
        out.extend(body)
        out.append("")
        out.append("</details>")
        index = close + 1
    return "\n".join(out)


# The "Run it" note claims JupyterLab is needed "for full MyST rendering" and
# that Colab shows "simplified formatting". Portable source makes both false:
# JupyterLab no longer needs jupyterlab-myst, and Colab renders the collapsibles
# and callouts. Only the fixed opening is rewritten; the trailing sentence is
# specific to each notebook and is preserved.
RUN_IT_RE = re.compile(
    r"^(>\s*\*\*Run it:\*\*)\s*use \[JupyterLab locally\]\(local_setup\.md\)"
    r" for full MyST rendering(?: and executable cells)?,"
    r" or \[open in Google Colab\]\(([^)]+)\)"
    r" for zero setup with simplified formatting\.\s*(.*)$",
    re.MULTILINE,
)


def rewrite_run_it(source: str) -> tuple[str, int]:
    """Return the cell with the launch note re-worded, and how many it changed."""

    def replace(match: re.Match) -> str:
        prefix, colab_url, tail = match.groups()
        tail = f" {tail.strip()}" if tail.strip() else ""
        return (
            f"{prefix} use [JupyterLab locally](local_setup.md), "
            f"or [open in Google Colab]({colab_url}) for zero setup.{tail}"
        )

    return RUN_IT_RE.subn(replace, source)


def convert_cell(source: str, where: str) -> str:
    """Admonitions first: one of them lives inside a dropdown."""
    source, _ = rewrite_run_it(source)
    return convert_dropdowns(convert_admonitions(source, where), where)


def convert_notebook(path: Path, write: bool) -> tuple[int, int, int]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    dropdowns = admonitions = run_it = 0
    changed = False

    for number, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "markdown":
            continue
        source = cell["source"]
        source = source if isinstance(source, str) else "".join(source)
        if not (
            DIRECTIVE_OPEN_RE.search(source)
            or ADMONITION_OPEN_RE.search(source)
            or RUN_IT_RE.search(source)
        ):
            continue

        run_it += len(RUN_IT_RE.findall(source))
        where = f"{path.name} cell {number}"
        dropdowns += len(re.findall(r"^:{3,}\{dropdown\}", source, re.M))
        admonitions += len(
            [
                m
                for m in re.findall(r"^`{3,}\{([a-z-]+)\}", source, re.M)
                if m in ADMONITION_LABELS
            ]
        )
        converted = convert_cell(source, where)
        if converted != source:
            cell["source"] = converted.splitlines(keepends=True)
            changed = True

    if write and changed:
        path.write_text(
            json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return dropdowns, admonitions, run_it


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("notebooks", nargs="+", type=Path)
    parser.add_argument(
        "--check", action="store_true", help="Report what would change, write nothing."
    )
    args = parser.parse_args()

    failures = []
    total_dropdowns = total_admonitions = total_run_it = 0
    for path in args.notebooks:
        try:
            dropdowns, admonitions, run_it = convert_notebook(path, write=not args.check)
        except ConversionError as error:
            failures.append(str(error))
            continue
        total_dropdowns += dropdowns
        total_admonitions += admonitions
        total_run_it += run_it
        if dropdowns or admonitions or run_it:
            verb = "would convert" if args.check else "converted"
            print(
                f"  {path.name}: {verb} {dropdowns} dropdowns, {admonitions} admonitions,"
                f" {run_it} launch note"
            )
        elif path.name.endswith(".ipynb"):
            print(f"  {path.name}: nothing to convert")

    print(
        f"\nTotal: {total_dropdowns} dropdowns, {total_admonitions} admonitions,"
        f" {total_run_it} launch notes"
    )
    if failures:
        print(f"\n{len(failures)} notebook(s) need a source fix first:", file=sys.stderr)
        for failure in failures:
            print(f"  ERROR {failure}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
