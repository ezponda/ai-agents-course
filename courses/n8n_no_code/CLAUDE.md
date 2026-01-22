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

### 5. Links
- Check that documentation links work (n8n docs change frequently)
- Manual Trigger docs: `https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.manualworkflowtrigger/`

### 6. If You Rename or Delete a Workflow
Search all `.ipynb` files for references and update them:
```bash
grep -r "filename.json" courses/n8n_no_code/book/
```

## Verification Script

Run this to check for broken references and prompt consistency:
```bash
python3 courses/n8n_no_code/check_references.py
```

**What it checks:**
1. All JSON workflow references in notebooks exist
2. All workflow JSON files are valid
3. Documented prompts match actual workflow prompts (warns if mismatch)
4. Reports unreferenced workflows

### 7. Documenting Prompts

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

### 8. Import URL + Download Pattern

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

## Common Edits

**Add a new workflow example:**
1. Add JSON to `book/_static/workflows/`
2. Add section in the relevant `.ipynb` with GitHub link
3. Include node-by-node table with actual node names
4. Include data flow diagram showing INPUT → OUTPUT
5. Run `make build-n8n` to verify

**Fix a broken link:**
1. Search: `grep -r "old-url" courses/n8n_no_code/book/`
2. Replace in all files
3. Rebuild and verify

## Style Notes

- No cost warnings in every section (one note in intro is enough)
- No emojis unless the user requests them
- Expressions in prose should use backticks: `{{ $json.field }}`
- Tables are preferred over long lists
