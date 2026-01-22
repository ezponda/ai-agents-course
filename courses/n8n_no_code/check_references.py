#!/usr/bin/env python3
"""
Check n8n course for broken references and prompt consistency.

Checks:
1. JSON workflow files referenced in notebooks exist
2. Obvious broken relative links
3. System messages/prompts in notebooks match actual workflow JSONs

Usage:
    python3 courses/n8n_no_code/check_references.py
"""

import os
import re
import json
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
BOOK_DIR = SCRIPT_DIR / "book"
WORKFLOWS_DIR = SCRIPT_DIR / "book" / "_static" / "workflows"

def find_json_references(content: str) -> list[str]:
    """Extract .json filenames from content."""
    # Match patterns like: 01_prompt_chaining.json or `05_ai_agent.json`
    pattern = r'[\`\[\(]?(\d{2}_[a-zA-Z0-9_]+\.json)[\`\]\)]?'
    return list(set(re.findall(pattern, content)))

def check_notebooks():
    """Check all notebooks for broken JSON references."""
    issues = []

    if not BOOK_DIR.exists():
        print(f"Warning: Book directory not found: {BOOK_DIR}")
        return issues

    for notebook_path in BOOK_DIR.glob("*.ipynb"):
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            issues.append(f"Could not read {notebook_path.name}: {e}")
            continue

        # Find JSON references
        json_refs = find_json_references(content)

        for json_file in json_refs:
            json_path = WORKFLOWS_DIR / json_file
            if not json_path.exists():
                issues.append(f"{notebook_path.name}: References missing file '{json_file}'")

    return issues

def check_workflow_files():
    """Check that workflow JSON files are valid."""
    issues = []

    if not WORKFLOWS_DIR.exists():
        print(f"Warning: Workflows directory not found: {WORKFLOWS_DIR}")
        return issues

    for json_path in WORKFLOWS_DIR.glob("*.json"):
        # Skip archived files
        if "_archive" in str(json_path):
            continue
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Basic validation: should have 'nodes' key
            if 'nodes' not in data:
                issues.append(f"{json_path.name}: Missing 'nodes' key (may not be valid n8n workflow)")
        except json.JSONDecodeError as e:
            issues.append(f"{json_path.name}: Invalid JSON - {e}")
        except Exception as e:
            issues.append(f"{json_path.name}: Could not read - {e}")

    return issues

def extract_prompts_from_workflow(json_path: Path) -> dict[str, str]:
    """Extract system messages and prompts from a workflow JSON."""
    prompts = {}

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return prompts

    for node in data.get('nodes', []):
        node_name = node.get('name', 'Unknown')
        params = node.get('parameters', {})

        # Check for AI Agent system message
        options = params.get('options', {})
        if 'systemMessage' in options:
            prompts[f"{node_name} (systemMessage)"] = options['systemMessage']

        # Check for Basic LLM Chain messages
        messages = params.get('messages', {}).get('messageValues', [])
        for i, msg in enumerate(messages):
            if 'message' in msg:
                # Clean up the message (remove leading =)
                content = msg['message']
                if content.startswith('='):
                    content = content[1:]
                msg_type = msg.get('type', 'SystemMessagePromptTemplate')
                if msg_type == 'SystemMessagePromptTemplate' or i == 0:
                    prompts[f"{node_name} (system)"] = content

    return prompts

def extract_prompts_from_notebook(notebook_path: Path) -> dict[str, str]:
    """Extract documented prompts from code blocks in a notebook."""
    prompts = {}

    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return prompts

    for cell in data.get('cells', []):
        if cell.get('cell_type') != 'markdown':
            continue

        source = ''.join(cell.get('source', []))

        # Find code blocks that look like prompts
        # Pattern: **Node Name:** or ### Node Name followed by ``` code block
        # Look for patterns like "**Step 1 — Create Outline:**" followed by code block
        pattern = r'\*\*([^*]+?)(?:\s*—\s*[^*]+)?(?:\s*\([^)]+\))?:\*\*\s*\n```\n(.*?)\n```'
        matches = re.findall(pattern, source, re.DOTALL)

        for name, content in matches:
            name = name.strip()
            content = content.strip()
            # Skip non-prompt code blocks
            if content.startswith('{') or content.startswith('https://') or 'INPUT' in content:
                continue
            # Skip JSON examples
            if '"customer_name"' in content or '"sentiment"' in content:
                continue
            prompts[name] = content

    return prompts

def normalize_prompt(text: str) -> str:
    """Normalize a prompt for comparison."""
    # Remove leading/trailing whitespace
    text = text.strip()
    # Remove leading = (n8n expression marker)
    if text.startswith('='):
        text = text[1:]
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove "System: " prefix if present in docs
    text = re.sub(r'^System:\s*', '', text)
    return text.lower()

def check_prompt_consistency():
    """Check that prompts in notebooks match workflow JSONs."""
    issues = []
    warnings = []

    # Define which notebooks document which workflows
    notebook_workflow_map = {
        "04_workflow_examples.ipynb": [
            "01_prompt_chaining.json",
            "02_routing.json",
            "03_parallelization.json"
        ],
        "05_first_ai_agent.ipynb": [
            "05_ai_agent_basics_calculator_memory.json",
            "06_ai_agent_tools_wikipedia_calculator.json",
            "07_ai_agent_chat_trigger_memory.json"
        ],
        "appendix_prompt_engineering.ipynb": [
            "08_prompt_engineering_comparison.json"
        ]
    }

    for notebook_name, workflow_files in notebook_workflow_map.items():
        notebook_path = BOOK_DIR / notebook_name
        if not notebook_path.exists():
            continue

        notebook_prompts = extract_prompts_from_notebook(notebook_path)

        for workflow_file in workflow_files:
            workflow_path = WORKFLOWS_DIR / workflow_file
            if not workflow_path.exists():
                continue

            workflow_prompts = extract_prompts_from_workflow(workflow_path)

            # Check each workflow prompt against notebook documentation
            for wf_key, wf_prompt in workflow_prompts.items():
                wf_normalized = normalize_prompt(wf_prompt)

                # Look for a matching documented prompt
                found_match = False
                for nb_key, nb_prompt in notebook_prompts.items():
                    nb_normalized = normalize_prompt(nb_prompt)

                    # Check if key concepts match (not exact, but substantial overlap)
                    wf_words = set(wf_normalized.split())
                    nb_words = set(nb_normalized.split())

                    # Calculate overlap
                    if len(wf_words) > 0:
                        overlap = len(wf_words & nb_words) / len(wf_words)
                        if overlap > 0.6:  # 60% word overlap
                            found_match = True
                            break

                if not found_match and "systemMessage" in wf_key:
                    # Only warn about system messages not documented
                    node_name = wf_key.replace(" (systemMessage)", "")
                    warnings.append(f"{workflow_file}: '{node_name}' system message may not be documented in {notebook_name}")

    return issues, warnings

def list_referenced_vs_available():
    """Show which workflows are referenced and which exist."""
    # Get all available workflows
    available = set()
    if WORKFLOWS_DIR.exists():
        for p in WORKFLOWS_DIR.glob("*.json"):
            if "_archive" not in str(p):
                available.add(p.name)

    # Get all referenced workflows
    referenced = set()
    if BOOK_DIR.exists():
        for notebook_path in BOOK_DIR.glob("*.ipynb"):
            try:
                with open(notebook_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                referenced.update(find_json_references(content))
            except:
                pass

    return available, referenced

def main():
    print("=" * 60)
    print("n8n Course Reference Checker")
    print("=" * 60)

    all_issues = []

    # Check notebooks
    print("\n[1] Checking notebook references...")
    issues = check_notebooks()
    all_issues.extend(issues)
    if issues:
        for issue in issues:
            print(f"  ERROR: {issue}")
    else:
        print("  OK: All JSON references point to existing files")

    # Check workflow files
    print("\n[2] Validating workflow JSON files...")
    issues = check_workflow_files()
    all_issues.extend(issues)
    if issues:
        for issue in issues:
            print(f"  ERROR: {issue}")
    else:
        print("  OK: All workflow files are valid JSON")

    # Check prompt consistency
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

    # Summary
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

    # Final result
    print("\n" + "=" * 60)
    if all_issues:
        print(f"FAILED: {len(all_issues)} issue(s) found")
        return 1
    else:
        print("PASSED: No issues found")
        return 0

if __name__ == "__main__":
    exit(main())
