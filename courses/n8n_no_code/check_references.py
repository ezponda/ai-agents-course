#!/usr/bin/env python3
"""
Check n8n course for broken references, consistency, and structure.

Checks:
 1. JSON workflow files referenced in notebooks exist
 2. Workflow JSON files are valid and have 'nodes' key
 3. Documented prompts match actual workflow prompts (60 % word overlap)
 4. Reference summary (unreferenced / missing workflows)
 5. _toc.yml ↔ Course Structure table in 00_introduction.ipynb
 6. Title naming conventions (Appendix A–Z, Project 1–N, no accidental prefixes)
 7. Workflow-documenting notebooks have import URL, download, build-from-scratch
 8. {download} directives point to existing files
 9. Sticky notes in workflow JSONs have valid ezponda.github.io URLs
10. (Optional, --check-urls) HEAD-request all external URLs

Usage:
    python3 courses/n8n_no_code/check_references.py              # checks 1-9
    python3 courses/n8n_no_code/check_references.py --check-urls  # checks 1-10
"""

import argparse
import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
BOOK_DIR = SCRIPT_DIR / "book"
WORKFLOWS_DIR = SCRIPT_DIR / "book" / "_static" / "workflows"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_notebook_cache: dict[str, dict] = {}


def read_notebook(path: Path) -> dict:
    """Parse an .ipynb file and return its dict.  Results are cached."""
    key = str(path)
    if key not in _notebook_cache:
        with open(path, "r", encoding="utf-8") as f:
            _notebook_cache[key] = json.load(f)
    return _notebook_cache[key]


def get_notebook_markdown(nb_data: dict) -> str:
    """Join all markdown cell sources into one string."""
    parts: list[str] = []
    for cell in nb_data.get("cells", []):
        if cell.get("cell_type") == "markdown":
            parts.append("".join(cell.get("source", [])))
    return "\n\n".join(parts)


def find_json_references(content: str) -> list[str]:
    """Extract .json filenames from content."""
    pattern = r'[\`\[\(> /]([a-zA-Z0-9][a-zA-Z0-9_]*\.json)[\`\]\) \n,]'
    return list(set(re.findall(pattern, content)))


# ---------------------------------------------------------------------------
# Check 1 — notebook JSON references
# ---------------------------------------------------------------------------
def check_notebooks():
    """Check all notebooks for broken JSON references."""
    issues = []

    if not BOOK_DIR.exists():
        print(f"  Warning: Book directory not found: {BOOK_DIR}")
        return issues

    for notebook_path in sorted(BOOK_DIR.glob("*.ipynb")):
        try:
            with open(notebook_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            issues.append(f"Could not read {notebook_path.name}: {e}")
            continue

        json_refs = find_json_references(content)
        for json_file in json_refs:
            json_path = WORKFLOWS_DIR / json_file
            if not json_path.exists():
                issues.append(
                    f"{notebook_path.name}: References missing file '{json_file}'"
                )

    return issues


# ---------------------------------------------------------------------------
# Check 2 — workflow JSON validity
# ---------------------------------------------------------------------------
def check_workflow_files():
    """Check that workflow JSON files are valid."""
    issues = []

    if not WORKFLOWS_DIR.exists():
        print(f"  Warning: Workflows directory not found: {WORKFLOWS_DIR}")
        return issues

    for json_path in sorted(WORKFLOWS_DIR.glob("*.json")):
        if "_archive" in str(json_path):
            continue
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "nodes" not in data:
                issues.append(
                    f"{json_path.name}: Missing 'nodes' key "
                    "(may not be valid n8n workflow)"
                )
        except json.JSONDecodeError as e:
            issues.append(f"{json_path.name}: Invalid JSON - {e}")
        except Exception as e:
            issues.append(f"{json_path.name}: Could not read - {e}")

    return issues


# ---------------------------------------------------------------------------
# Check 3 — prompt consistency
# ---------------------------------------------------------------------------
def extract_prompts_from_workflow(json_path: Path) -> dict[str, str]:
    """Extract system messages and prompts from a workflow JSON."""
    prompts = {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return prompts

    for node in data.get("nodes", []):
        node_name = node.get("name", "Unknown")
        params = node.get("parameters", {})

        options = params.get("options", {})
        if "systemMessage" in options:
            prompts[f"{node_name} (systemMessage)"] = options["systemMessage"]

        messages = params.get("messages", {}).get("messageValues", [])
        for i, msg in enumerate(messages):
            if "message" in msg:
                content = msg["message"]
                if content.startswith("="):
                    content = content[1:]
                msg_type = msg.get("type", "SystemMessagePromptTemplate")
                if msg_type == "SystemMessagePromptTemplate" or i == 0:
                    prompts[f"{node_name} (system)"] = content

    return prompts


def extract_prompts_from_notebook(notebook_path: Path) -> dict[str, str]:
    """Extract documented prompts from code blocks in a notebook."""
    prompts = {}
    try:
        nb_data = read_notebook(notebook_path)
    except Exception:
        return prompts

    for cell in nb_data.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue

        source = "".join(cell.get("source", []))
        pattern = (
            r'\*\*([^*]+?)(?:\s*—\s*[^*]+)?(?:\s*\([^)]+\))?:\*\*'
            r'\s*\n```\n(.*?)\n```'
        )
        matches = re.findall(pattern, source, re.DOTALL)

        for name, content in matches:
            name = name.strip()
            content = content.strip()
            if content.startswith("{") or content.startswith("https://") or "INPUT" in content:
                continue
            if '"customer_name"' in content or '"sentiment"' in content:
                continue
            prompts[name] = content

    return prompts


def normalize_prompt(text: str) -> str:
    """Normalize a prompt for comparison."""
    text = text.strip()
    if text.startswith("="):
        text = text[1:]
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^System:\s*", "", text)
    return text.lower()


# Map of notebooks → workflow files they document
NOTEBOOK_WORKFLOW_MAP = {
    "04a_prompt_chaining.ipynb": ["01_prompt_chaining.json"],
    "04b_routing.ipynb": ["02_routing.json"],
    "04c_parallelization.ipynb": ["03_parallelization.json"],
    "04d_human_in_the_loop.ipynb": ["04_human_in_the_loop.json"],
    "06_first_ai_agent.ipynb": [
        "05_ai_agent_basics_calculator_memory.json",
        "06_ai_agent_tools_wikipedia_calculator.json",
        "07_ai_agent_chat_trigger_memory.json",
    ],
    "appendix_d_prompt_engineering.ipynb": [
        "08_prompt_engineering_comparison.json",
    ],
    "project_1_recipe_assistant.ipynb": [
        "10a_shopping_list_agent.json",
        "10b_recipe_assistant.json",
    ],
    "appendix_b_going_live.ipynb": [
        "going_live_schedule.json",
        "going_live_webhook.json",
        "going_live_error.json",
    ],
}


def check_prompt_consistency():
    """Check that prompts in notebooks match workflow JSONs."""
    issues = []
    warnings = []

    for notebook_name, workflow_files in NOTEBOOK_WORKFLOW_MAP.items():
        notebook_path = BOOK_DIR / notebook_name
        if not notebook_path.exists():
            continue

        notebook_prompts = extract_prompts_from_notebook(notebook_path)

        for workflow_file in workflow_files:
            workflow_path = WORKFLOWS_DIR / workflow_file
            if not workflow_path.exists():
                continue

            workflow_prompts = extract_prompts_from_workflow(workflow_path)

            for wf_key, wf_prompt in workflow_prompts.items():
                wf_normalized = normalize_prompt(wf_prompt)
                found_match = False

                for _nb_key, nb_prompt in notebook_prompts.items():
                    nb_normalized = normalize_prompt(nb_prompt)
                    wf_words = set(wf_normalized.split())
                    nb_words = set(nb_normalized.split())

                    if len(wf_words) > 0:
                        overlap = len(wf_words & nb_words) / len(wf_words)
                        if overlap > 0.6:
                            found_match = True
                            break

                if not found_match and "systemMessage" in wf_key:
                    node_name = wf_key.replace(" (systemMessage)", "")
                    warnings.append(
                        f"{workflow_file}: '{node_name}' system message "
                        f"may not be documented in {notebook_name}"
                    )

    return issues, warnings


# ---------------------------------------------------------------------------
# Check 4 — referenced vs available
# ---------------------------------------------------------------------------
def list_referenced_vs_available():
    """Show which workflows are referenced and which exist."""
    available: set[str] = set()
    if WORKFLOWS_DIR.exists():
        for p in WORKFLOWS_DIR.glob("*.json"):
            if "_archive" not in str(p):
                available.add(p.name)

    referenced: set[str] = set()
    if BOOK_DIR.exists():
        for notebook_path in BOOK_DIR.glob("*.ipynb"):
            try:
                with open(notebook_path, "r", encoding="utf-8") as f:
                    content = f.read()
                referenced.update(find_json_references(content))
            except Exception:
                pass

    return available, referenced


# ---------------------------------------------------------------------------
# Check 5 — TOC ↔ intro table sync
# ---------------------------------------------------------------------------
def _parse_toc() -> dict[str, list[str]]:
    """Return {section_caption: [file_stem, ...]} from _toc.yml.

    Only collects chapter-level files (indented ≤ 6 spaces), not section
    sub-pages which appear in the sidebar automatically.
    """
    toc_path = BOOK_DIR / "_toc.yml"
    sections: dict[str, list[str]] = {}
    current_caption: str | None = None
    with open(toc_path, "r", encoding="utf-8") as f:
        for line in f:
            cap_match = re.match(r"\s*-\s*caption:\s*(.+)", line)
            if cap_match:
                current_caption = cap_match.group(1).strip()
                sections[current_caption] = []
                continue
            # Only match chapter-level files (≤ 6 leading spaces), skip
            # deeper "sections:" entries which are sub-pages.
            file_match = re.match(r"(\s*)-\s*file:\s*(.+)", line)
            if file_match and current_caption is not None:
                indent = len(file_match.group(1))
                if indent <= 6:
                    sections[current_caption].append(file_match.group(2).strip())
    return sections


def _parse_intro_table() -> dict[str, list[str]]:
    """Return {section: [file_stem, ...]} from the Course Structure cell.

    Maps intro table rows back to file stems using the TOC for lookup.
    """
    intro_path = BOOK_DIR / "00_introduction.ipynb"
    nb_data = read_notebook(intro_path)

    # Find the Course Structure cell
    structure_text = ""
    for cell in nb_data.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        src = "".join(cell.get("source", []))
        if "## Course Structure" in src:
            structure_text = src
            break

    if not structure_text:
        return {}

    # Build a map from readable title → file stem using TOC + notebook titles
    toc_sections = _parse_toc()
    title_to_stem: dict[str, str] = {}
    for _section, stems in toc_sections.items():
        for stem in stems:
            nb_path = BOOK_DIR / f"{stem}.ipynb"
            if nb_path.exists():
                try:
                    nd = read_notebook(nb_path)
                    md = get_notebook_markdown(nd)
                    m = re.match(r"#\s+(.+)", md)
                    if m:
                        raw_title = m.group(1).strip()
                        # Strip prefix like "Appendix A: " or "Project 1: "
                        cleaned = re.sub(
                            r"^(?:Appendix\s+[A-Z]:\s*|Project\s+\d+:\s*)", "", raw_title
                        )
                        title_to_stem[cleaned.lower()] = stem
                        title_to_stem[raw_title.lower()] = stem
                except Exception:
                    pass

    # Parse table rows — look for bold text in first column
    sections: dict[str, list[str]] = {"Course": [], "Projects": [], "Appendices": []}
    current_section: str | None = None
    for line in structure_text.splitlines():
        if line.strip().startswith("### Course"):
            current_section = "Course"
            continue
        if line.strip().startswith("### Projects"):
            current_section = "Projects"
            continue
        if line.strip().startswith("### Appendices"):
            current_section = "Appendices"
            continue

        if current_section is None:
            continue

        # Table row: | **Title** | description |
        row_match = re.match(r"\|\s*\*\*(.+?)\*\*\s*\|", line)
        if not row_match:
            continue

        title_text = row_match.group(1).strip()
        # Strip "Appendix X: " or "Project N: " prefix for lookup
        cleaned = re.sub(
            r"^(?:Appendix\s+[A-Z]:\s*|Project\s+\d+:\s*)", "", title_text
        )
        key = cleaned.lower()

        stem = title_to_stem.get(key) or title_to_stem.get(title_text.lower())
        if stem:
            sections[current_section].append(stem)
        else:
            # Fallback: fuzzy match
            for t, s in title_to_stem.items():
                if key in t or t in key:
                    sections[current_section].append(s)
                    break
            else:
                sections[current_section].append(f"??{title_text}")

    return sections


def check_toc_sync():
    """Verify _toc.yml matches the Course Structure table in 00_introduction."""
    issues: list[str] = []

    toc_path = BOOK_DIR / "_toc.yml"
    intro_path = BOOK_DIR / "00_introduction.ipynb"
    if not toc_path.exists() or not intro_path.exists():
        issues.append("Missing _toc.yml or 00_introduction.ipynb")
        return issues

    toc_sections = _parse_toc()
    intro_sections = _parse_intro_table()

    if not intro_sections:
        issues.append("Could not find Course Structure table in 00_introduction.ipynb")
        return issues

    # Map TOC caption → intro section key
    caption_map = {
        "Course": "Course",
        "Projects": "Projects",
        "Appendices": "Appendices",
    }

    for caption, intro_key in caption_map.items():
        toc_files = set(toc_sections.get(caption, []))
        intro_files = set(intro_sections.get(intro_key, []))
        # Filter out unresolved entries
        intro_files = {f for f in intro_files if not f.startswith("??")}

        in_toc_not_intro = toc_files - intro_files
        in_intro_not_toc = intro_files - toc_files

        for f in sorted(in_toc_not_intro):
            issues.append(
                f"'{f}' is in _toc.yml ({caption}) but missing from intro table"
            )
        for f in sorted(in_intro_not_toc):
            issues.append(
                f"'{f}' is in intro table ({intro_key}) but missing from _toc.yml"
            )

    return issues


# ---------------------------------------------------------------------------
# Check 6 — title naming conventions
# ---------------------------------------------------------------------------
def check_title_patterns():
    """Verify naming conventions for appendix, project, and course notebooks."""
    issues: list[str] = []
    warnings: list[str] = []

    toc_sections = _parse_toc()

    # --- Appendices: must be "# Appendix [A-Z]: ..." in sequential order ---
    appendix_stems = toc_sections.get("Appendices", [])
    expected_letter = ord("A")
    for stem in appendix_stems:
        nb_path = BOOK_DIR / f"{stem}.ipynb"
        if not nb_path.exists():
            issues.append(f"{stem}.ipynb: file not found")
            continue
        nb_data = read_notebook(nb_path)
        md = get_notebook_markdown(nb_data)
        m = re.match(r"#\s+Appendix\s+([A-Z]):\s+", md)
        if not m:
            issues.append(
                f"{stem}.ipynb: title must match '# Appendix [A-Z]: ...'"
            )
            continue
        actual_letter = m.group(1)
        if ord(actual_letter) != expected_letter:
            issues.append(
                f"{stem}.ipynb: expected Appendix {chr(expected_letter)}, "
                f"found Appendix {actual_letter}"
            )
        expected_letter += 1

    # --- Projects: must be "# Project \d+: ..." in sequential order ---
    project_stems = toc_sections.get("Projects", [])
    expected_num = 1
    for stem in project_stems:
        nb_path = BOOK_DIR / f"{stem}.ipynb"
        if not nb_path.exists():
            issues.append(f"{stem}.ipynb: file not found")
            continue
        nb_data = read_notebook(nb_path)
        md = get_notebook_markdown(nb_data)
        m = re.match(r"#\s+Project\s+(\d+):\s+", md)
        if not m:
            issues.append(
                f"{stem}.ipynb: title must match '# Project N: ...'"
            )
            continue
        actual_num = int(m.group(1))
        if actual_num != expected_num:
            issues.append(
                f"{stem}.ipynb: expected Project {expected_num}, "
                f"found Project {actual_num}"
            )
        expected_num += 1

    # --- Course chapters: warn if they accidentally say "Appendix" or "Project" ---
    course_stems = toc_sections.get("Course", [])
    for stem in course_stems:
        nb_path = BOOK_DIR / f"{stem}.ipynb"
        if not nb_path.exists():
            continue
        nb_data = read_notebook(nb_path)
        md = get_notebook_markdown(nb_data)
        m = re.match(r"#\s+(.+)", md)
        if m:
            title = m.group(1).strip()
            if re.match(r"Appendix\s+[A-Z]:", title):
                warnings.append(
                    f"{stem}.ipynb: course chapter has 'Appendix' prefix"
                )
            if re.match(r"Project\s+\d+:", title):
                warnings.append(
                    f"{stem}.ipynb: course chapter has 'Project' prefix"
                )

    return issues, warnings


# ---------------------------------------------------------------------------
# Check 7 — notebook structure (import URL, download, build-from-scratch)
# ---------------------------------------------------------------------------
def check_notebook_structure():
    """Verify workflow-documenting notebooks have required elements."""
    issues: list[str] = []
    warnings: list[str] = []

    for notebook_name, workflow_files in NOTEBOOK_WORKFLOW_MAP.items():
        nb_path = BOOK_DIR / notebook_name
        if not nb_path.exists():
            continue

        try:
            nb_data = read_notebook(nb_path)
        except Exception:
            issues.append(f"{notebook_name}: could not read notebook")
            continue

        md = get_notebook_markdown(nb_data)

        for wf_file in workflow_files:
            # Import URL
            raw_url_fragment = (
                f"raw.githubusercontent.com/ezponda/ai-agents-course/"
                f"main/courses/n8n_no_code/book/_static/workflows/{wf_file}"
            )
            if raw_url_fragment not in md:
                issues.append(
                    f"{notebook_name}: missing import URL for {wf_file}"
                )

            # Download directive
            download_pattern = (
                r"\{download\}`[^`]*" + re.escape(wf_file) + r"[^`]*`"
            )
            if not re.search(download_pattern, md):
                issues.append(
                    f"{notebook_name}: missing {{download}} directive for {wf_file}"
                )

        # Build-from-scratch dropdown (🛠️)
        # Appendix notebooks may legitimately skip this, so warn rather than error
        if "🛠️" not in md:
            warnings.append(
                f"{notebook_name}: missing build-from-scratch dropdown (🛠️)"
            )

    return issues, warnings


# ---------------------------------------------------------------------------
# Check 8 — {download} directives point to existing files
# ---------------------------------------------------------------------------
def check_download_directives():
    """Verify {download} directives resolve to existing files."""
    issues: list[str] = []

    if not BOOK_DIR.exists():
        return issues

    pattern = re.compile(r"\{download\}`[^<]*<([^>]+)>`")

    for nb_path in sorted(BOOK_DIR.glob("*.ipynb")):
        try:
            with open(nb_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        for m in pattern.finditer(content):
            rel_path = m.group(1)
            target = (BOOK_DIR / rel_path).resolve()
            if not target.exists():
                issues.append(
                    f"{nb_path.name}: {{download}} target not found: {rel_path}"
                )

    return issues


# ---------------------------------------------------------------------------
# Check 9 — sticky notes in workflow JSONs
# ---------------------------------------------------------------------------
def check_sticky_notes():
    """Verify sticky note URLs in workflow JSONs."""
    issues: list[str] = []
    warnings: list[str] = []

    if not WORKFLOWS_DIR.exists():
        return issues, warnings

    build_html = BOOK_DIR / "_build" / "html"

    for json_path in sorted(WORKFLOWS_DIR.glob("*.json")):
        if "_archive" in str(json_path):
            continue
        # Skip screenshot helper workflows
        if "00_screenshot" in json_path.name:
            continue

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        nodes = data.get("nodes", [])
        sticky_nodes = [
            n for n in nodes
            if n.get("type") == "n8n-nodes-base.stickyNote"
        ]

        # Must have at least one stickyNote with ezponda.github.io URL
        found_course_url = False
        for sn in sticky_nodes:
            content = sn.get("parameters", {}).get("content", "")
            url_match = re.search(
                r"https://ezponda\.github\.io/ai-agents-course/([^)\s\"#]+)"
                r"(?:#([^)\s\"]*))?",
                content,
            )
            if not url_match:
                continue

            found_course_url = True
            page_part = url_match.group(1)  # e.g. "04_workflow_examples.html"
            fragment = url_match.group(2)    # e.g. "pattern-1-prompt-chaining"

            # Check page corresponds to a notebook
            if page_part.endswith(".html"):
                stem = page_part[:-5]  # strip .html
                nb_file = BOOK_DIR / f"{stem}.ipynb"
                if not nb_file.exists():
                    issues.append(
                        f"{json_path.name}: sticky note URL references "
                        f"'{stem}.ipynb' which does not exist"
                    )

            # If build exists, verify anchor
            if fragment and build_html.exists():
                html_file = build_html / page_part
                if html_file.exists():
                    try:
                        html_content = html_file.read_text(encoding="utf-8")
                        if f'id="{fragment}"' not in html_content:
                            warnings.append(
                                f"{json_path.name}: anchor '#{fragment}' "
                                f"not found in built HTML {page_part}"
                            )
                    except Exception:
                        pass

        if not found_course_url:
            issues.append(
                f"{json_path.name}: no stickyNote with ezponda.github.io URL"
            )

    return issues, warnings


# ---------------------------------------------------------------------------
# Check 10 — external URL check (opt-in)
# ---------------------------------------------------------------------------
def check_external_urls():
    """HEAD-request all external URLs found in notebooks."""
    import urllib.request
    import urllib.error

    issues: list[str] = []
    warnings: list[str] = []

    if not BOOK_DIR.exists():
        return issues, warnings

    # Collect all URLs
    url_pattern = re.compile(r"https://[^\s\"\'\)\]\\>`]+")
    all_urls: set[str] = set()

    for nb_path in sorted(BOOK_DIR.glob("*.ipynb")):
        try:
            with open(nb_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue
        for m in url_pattern.finditer(content):
            url = m.group(0).rstrip(".,;:")
            all_urls.add(url)

    # Filter
    skip_hosts = {"localhost", "127.0.0.1"}
    filtered: list[str] = []
    for url in sorted(all_urls):
        host_match = re.match(r"https://([^/:]+)", url)
        if host_match and host_match.group(1) in skip_hosts:
            continue
        filtered.append(url)

    print(f"  Checking {len(filtered)} unique URLs...")

    for url in filtered:
        try:
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", "n8n-course-checker/1.0")
            resp = urllib.request.urlopen(req, timeout=5)
            code = resp.getcode()
            if code and code >= 400:
                warnings.append(f"HTTP {code}: {url}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                issues.append(f"404 Not Found: {url}")
            elif e.code == 405:
                # Method not allowed — try GET
                try:
                    req2 = urllib.request.Request(url, method="GET")
                    req2.add_header("User-Agent", "n8n-course-checker/1.0")
                    resp2 = urllib.request.urlopen(req2, timeout=5)
                    code2 = resp2.getcode()
                    if code2 and code2 >= 400:
                        warnings.append(f"HTTP {code2}: {url}")
                    # Read a small amount to avoid hanging
                    resp2.read(1024)
                    resp2.close()
                except Exception:
                    pass  # 405 is common, don't report if GET also fails
            else:
                warnings.append(f"HTTP {e.code}: {url}")
        except urllib.error.URLError as e:
            warnings.append(f"Connection error: {url} ({e.reason})")
        except Exception as e:
            warnings.append(f"Error: {url} ({e})")

    return issues, warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Check n8n course for broken references and consistency."
    )
    parser.add_argument(
        "--check-urls",
        action="store_true",
        help="Also check external URLs (slow, hits the network).",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("n8n Course Reference Checker")
    print("=" * 60)

    all_issues: list[str] = []

    # ------------------------------------------------------------------
    # Check 1
    # ------------------------------------------------------------------
    print("\n[1] Checking notebook references...")
    issues = check_notebooks()
    all_issues.extend(issues)
    if issues:
        for issue in issues:
            print(f"  ERROR: {issue}")
    else:
        print("  OK: All JSON references point to existing files")

    # ------------------------------------------------------------------
    # Check 2
    # ------------------------------------------------------------------
    print("\n[2] Validating workflow JSON files...")
    issues = check_workflow_files()
    all_issues.extend(issues)
    if issues:
        for issue in issues:
            print(f"  ERROR: {issue}")
    else:
        print("  OK: All workflow files are valid JSON")

    # ------------------------------------------------------------------
    # Check 3
    # ------------------------------------------------------------------
    print("\n[3] Checking prompt documentation consistency...")
    issues, warnings = check_prompt_consistency()
    all_issues.extend(issues)
    if issues:
        for issue in issues:
            print(f"  ERROR: {issue}")
    if warnings:
        for warning in warnings:
            print(f"  WARNING: {warning}")
    if not issues and not warnings:
        print("  OK: Documented prompts appear consistent with workflow files")

    # ------------------------------------------------------------------
    # Check 4
    # ------------------------------------------------------------------
    print("\n[4] Reference summary...")
    available, referenced = list_referenced_vs_available()
    unreferenced = available - referenced
    if unreferenced:
        print(f"  Note: {len(unreferenced)} workflow(s) not referenced in book:")
        for f in sorted(unreferenced):
            print(f"    - {f}")
    missing = referenced - available
    if missing:
        print(f"  ERROR: {len(missing)} referenced workflow(s) missing:")
        for f in sorted(missing):
            print(f"    - {f}")
        all_issues.extend([f"Missing workflow: {f}" for f in missing])

    # ------------------------------------------------------------------
    # Check 5
    # ------------------------------------------------------------------
    print("\n[5] Checking TOC ↔ intro table sync...")
    issues = check_toc_sync()
    all_issues.extend(issues)
    if issues:
        for issue in issues:
            print(f"  ERROR: {issue}")
    else:
        print("  OK: All _toc.yml entries match Course Structure table")

    # ------------------------------------------------------------------
    # Check 6
    # ------------------------------------------------------------------
    print("\n[6] Checking title naming conventions...")
    issues, warnings = check_title_patterns()
    all_issues.extend(issues)
    if issues:
        for issue in issues:
            print(f"  ERROR: {issue}")
    if warnings:
        for warning in warnings:
            print(f"  WARNING: {warning}")
    if not issues and not warnings:
        print("  OK: Title patterns are consistent")

    # ------------------------------------------------------------------
    # Check 7
    # ------------------------------------------------------------------
    print("\n[7] Checking notebook structure (import/download/build)...")
    issues, warnings = check_notebook_structure()
    all_issues.extend(issues)
    if issues:
        for issue in issues:
            print(f"  ERROR: {issue}")
    if warnings:
        for warning in warnings:
            print(f"  WARNING: {warning}")
    if not issues and not warnings:
        print("  OK: All workflow-documenting notebooks have required elements")

    # ------------------------------------------------------------------
    # Check 8
    # ------------------------------------------------------------------
    print("\n[8] Checking {download} directives...")
    issues = check_download_directives()
    all_issues.extend(issues)
    if issues:
        for issue in issues:
            print(f"  ERROR: {issue}")
    else:
        print("  OK: All {download} targets exist")

    # ------------------------------------------------------------------
    # Check 9
    # ------------------------------------------------------------------
    print("\n[9] Checking sticky notes in workflow JSONs...")
    issues, warnings = check_sticky_notes()
    all_issues.extend(issues)
    if issues:
        for issue in issues:
            print(f"  ERROR: {issue}")
    if warnings:
        for warning in warnings:
            print(f"  WARNING: {warning}")
    if not issues and not warnings:
        print("  OK: All workflow sticky notes have valid course URLs")

    # ------------------------------------------------------------------
    # Check 10 (opt-in)
    # ------------------------------------------------------------------
    if args.check_urls:
        print("\n[10] Checking external URLs (this may be slow)...")
        issues, warnings = check_external_urls()
        all_issues.extend(issues)
        if issues:
            for issue in issues:
                print(f"  ERROR: {issue}")
        if warnings:
            for warning in warnings:
                print(f"  WARNING: {warning}")
        if not issues and not warnings:
            print("  OK: All external URLs are reachable")
    else:
        print("\n[10] External URL check skipped (use --check-urls to enable)")

    # ------------------------------------------------------------------
    # Final result
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    if all_issues:
        print(f"FAILED: {len(all_issues)} issue(s) found")
        return 1
    else:
        print("PASSED: No issues found")
        return 0


if __name__ == "__main__":
    exit(main())
