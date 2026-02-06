# n8n Course — Claude Code Context

This file helps Claude Code maintain consistency when editing the student-facing n8n course.

## Quick Reference

**Build command:** `make build-n8n` (or `make clean-n8n && make build-n8n`)
**Book source:** `courses/n8n_no_code/book/*.ipynb`
**Workflow JSONs:** `courses/n8n_no_code/book/_static/workflows/*.json`
**Output:** `courses/n8n_no_code/book/_build/html/`

## Audience

Non-technical learners. Assume no prior coding experience.

## Quick-Check Habits

### 1. Language
- Use plain English. Avoid jargon unless defined.
- Prefer short sentences and bullet points over long paragraphs.
- When introducing a term (Trigger, Node, Expression), define it once, then use it consistently.

### 2. Terminology Consistency
These terms have specific meanings in n8n. Use them exactly:

| Term | Meaning |
|------|---------|
| **Trigger** | First node; starts the workflow |
| **Node** | One step in a workflow |
| **Connection** | Solid line = data flow; Dotted line = capability |
| **Execution** | One run of a workflow |
| **Output panel** | Right-side panel showing node results |
| **Pinned Data** | Frozen output for testing |
| **Expression** | Dynamic value using `{{ $json.field }}` |
| **AI Agent** | Node that loops and uses tools |
| **Tools** | Sub-nodes the agent can call (Calculator, Wikipedia) |
| **Memory** | Sub-node for conversation history |

### 3. Workflow References
When telling students to import a workflow, always include a direct GitHub link:

```markdown
**File:** [`01_prompt_chaining.json`](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/01_prompt_chaining.json)
```

**Base URL pattern:**
```
https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/{filename}.json
```

### 4. Field Names
- Basic LLM Chain outputs to `text`
- AI Agent outputs to `output`
- Always verify field names in the actual workflow JSON before documenting
- **Keep notebooks and workflow JSONs in sync.** If you change a prompt or field value in a notebook, update the corresponding workflow JSON too (and vice versa).

### 5. Links
- Check that documentation links work (n8n docs change frequently)
- Manual Trigger docs: `https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.manualworkflowtrigger/`

### 6. File Naming Conventions

| Category | Pattern | Example |
|----------|---------|---------|
| Course chapters | `NN_name.ipynb` | `01_setup.ipynb` |
| Projects | `project_N_name.ipynb` | `project_1_recipe_assistant.ipynb` |
| Appendices | `appendix_X_name.ipynb` (X = A–Z) | `appendix_a_node_toolbox.ipynb` |

Titles inside the notebook must match: `# Project 1: Recipe Assistant`, `# Appendix A: Node Toolbox`.

The verification script (check 6) enforces sequential letters/numbers.

### 7. If You Rename or Delete a Workflow JSON
Search all `.ipynb` files for references and update them:
```bash
grep -r "filename.json" courses/n8n_no_code/book/
```

### 8. If You Rename or Delete a Notebook
Update **all five** places:
1. `_toc.yml` — `file:` entry (stem without `.ipynb`)
2. `check_references.py` — `NOTEBOOK_WORKFLOW_MAP` key (if present)
3. Workflow JSON sticky notes — `ezponda.github.io/ai-agents-course/{stem}.html` URLs
4. Cross-references in other notebooks — Jupyter Book `[text](file_stem)` links
5. Course Structure table in `00_introduction.ipynb` (if title/position changed)

Then run `python3 courses/n8n_no_code/check_references.py` — it catches broken sticky-note URLs (check 9) and TOC/intro mismatches (check 5).

## Verification Script

Run this to check for broken references and prompt consistency:
```bash
python3 courses/n8n_no_code/check_references.py
```

**What it checks:**
1. All JSON workflow references in notebooks exist
2. All workflow JSON files are valid
3. Documented prompts match actual workflow prompts (warns if mismatch)
4. Reports unreferenced / missing workflows
5. `_toc.yml` ↔ Course Structure table in `00_introduction.ipynb`
6. Title naming conventions (Appendix A–Z, Project 1–N sequential)
7. Workflow-documenting notebooks have import URL, download, build-from-scratch
8. `{download}` directives point to existing files
9. Sticky notes in workflow JSONs have valid `ezponda.github.io` URLs
10. (Optional, `--check-urls`) HEAD-request all external URLs

### 9. Documenting Prompts

When adding a new workflow example, always document the actual prompts used:

```markdown
### System Message

\```
You are a concise assistant.

Rules:
- If the user asks for ANY arithmetic, ALWAYS use the Calculator tool.
- Keep the final answer short (max 5 lines).
\```
```

**Important:** Copy prompts exactly from the workflow JSON. The verification script checks for consistency.

### 10. Import URL + Download Pattern

For each workflow, provide both import and download options:

```markdown
> **Import via URL** (copy and paste in n8n → Import from URL):
> \```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/01_prompt_chaining.json
> \```
>
> **Download:** {download}`01_prompt_chaining.json <_static/workflows/01_prompt_chaining.json>`
```

**Raw URL pattern (for import):**
```
https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/{filename}.json
```

**Download syntax (MyST/Jupyter Book):**
```
{download}`filename.json <_static/workflows/filename.json>`
```

### 11. Workflow JSON Sticky Notes

Every workflow JSON must include a Sticky Note with:
1. **Course documentation link** at the top (first line)
2. **Title and description** of the workflow
3. **Position** moved up ~100px from nodes to avoid overlap

**Format:**
```json
{
  "parameters": {
    "content": "📖 [Course documentation](https://ezponda.github.io/ai-agents-course/04a_prompt_chaining.html)\n## Pattern Title\n**Goal:** ...",
    "height": 240,
    "width": 700
  },
  "position": [-1080, -520]
}
```

**Link patterns:**
- Workflow Examples: `https://ezponda.github.io/ai-agents-course/04{a,b,c,d}_{pattern_name}.html`
- AI Agent Examples: `https://ezponda.github.io/ai-agents-course/05_first_ai_agent.html#example-X-name`

**Anchor format:** Each workflow pattern has its own page (e.g., `04a_prompt_chaining.html`), so anchors are rarely needed. For other pages: header text in lowercase, spaces → hyphens.

### 12. Data Flow Dropdowns

For each workflow example in the notebooks, add a collapsible dropdown showing the detailed data transformation at each step.

**MyST syntax:**
```markdown
::::{dropdown} 🔍 See detailed data transformation at each step
:color: info

[ASCII diagram showing JSON at each node]

::::
```

**Requirements:**
- Place dropdown immediately after the main Data Flow section
- Show actual JSON fields (verify against workflow JSON)
- Include visual arrows showing transformation
- Explain key insights at the bottom

**Example content:**
```
┌─────────────────┐            ┌─────────────────┐
│  Node A         │───────────▶│  Node B         │
└─────────────────┘            └─────────────────┘
        │                             │
        ▼                             ▼
┌─────────────────┐            ┌─────────────────┐
│ { "input": "x" }│            │ { "output": "y" }│
└─────────────────┘            └─────────────────┘
```

### 13. Build from Scratch Dropdowns

Each workflow example should include a step-by-step tutorial dropdown that allows students to build the workflow manually instead of importing.

**MyST syntax:**
```markdown
::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow
...

### Step 2: Add the trigger and input
...

::::
```

**Requirements:**
- Place dropdown immediately after the Import/Download block (before "Meet the Node" or explanation sections)
- Color: `secondary` (grey)
- Use `🛠️` emoji in title
- Include step-by-step instructions with exact node configurations
- **Field values must match the workflow JSON exactly** (verify before documenting)
- **System messages/prompts must match the JSON exactly** (copy from JSON, not paraphrase)
- Use tables for field configurations when there are multiple fields
- Include connection instructions between nodes

**Example field table:**
```markdown
| Name | Value |
|------|-------|
| `ticket_subject` | `Refund request — charged twice` |
| `ticket_body` | `Hi team,\nI was charged twice...` |
```

**Example system message:**
```markdown
- System:
  \```
  You are a customer support specialist for refunds.
  Write a short, professional reply.

  Rules:
  - Acknowledge the issue
  - Ask for any missing info (only if needed)
  - Keep it under 120 words

  Output ONLY the reply.
  \```
```

### 14. Course Structure Table (Introduction)

The intro page (`00_introduction.ipynb`) has a "Course Structure" table that must stay in sync with `_toc.yml`.

When adding, removing, or renaming chapters:
1. Update `_toc.yml`
2. Update the table in `00_introduction.ipynb` (cell with "## Course Structure")

The table provides "What you'll do" descriptions that the TOC sidebar doesn't have, so keep both.

## Common Edits

**Add a new chapter:**
1. Create the `.ipynb` file
2. Add to `_toc.yml`
3. Update the Course Structure table in `00_introduction.ipynb`

**Add a new workflow example:**
1. Add JSON to `book/_static/workflows/`
2. **Add Sticky Note with course documentation link** (see section 9)
3. Add section in the relevant `.ipynb` with GitHub link
4. **Add "Build from scratch" dropdown** (see section 11) — verify all values match JSON
5. Include node-by-node table with actual node names
6. Include data flow diagram showing INPUT → OUTPUT
7. **Add dropdown with detailed data transformation** (see section 10)
8. Run `make build-n8n` to verify
9. Run `python3 courses/n8n_no_code/check_references.py` to verify prompts match

**Fix a broken link:**
1. Search: `grep -r "old-url" courses/n8n_no_code/book/`
2. Replace in all files
3. Rebuild and verify

## ⚠️ TODO List — MANDATORY on every commit ⚠️

There is a `TODO.md` file at the repo root. It is in `.gitignore` and never pushed.

**CRITICAL — EVERY TIME you create a git commit, you MUST:**
1. Read `TODO.md`
2. Show the user the pending tasks grouped by urgency (🔴 URGENTE, 🟡 MEDIO, 🟢 POCO URGENTE)
3. List just the **bold labels** of each `- [ ]` item
4. This is NON-NEGOTIABLE — never skip this step, even if it seems redundant

**When the user adds a task:** Add it to the appropriate urgency section in `TODO.md`.

**When a task is done:** Move it to `## Completed` with the date, changing `- [ ]` to `- [x]`.

## Style Notes

- No cost warnings in every section (one note in intro is enough)
- No emojis unless the user requests them
- Expressions in prose should use backticks: `{{ $json.field }}`
- Tables are preferred over long lists
