# Workflow Examples: Four Patterns

This chapter shows four workflow patterns that solve real problems. Three of the four patterns introduce a **new node** on top of what you already know (Edit Fields, Basic LLM Chain). Prompt Chaining uses only nodes you have seen before.

For each pattern you will: import the workflow, run it, and see the results. Every section starts with a brief description of what you are building and why.

**Note on credentials:** These workflows require API credentials for an AI provider (OpenRouter, OpenAI, or Google). If you do not have credentials set up, you can still explore the workflow structure and understand what each node would do.

---

**How to Import and Run a Workflow**

Each workflow in this chapter provides two ways to import it:

| Option | When to use |
|--------|-------------|
| **Import via URL** | Fastest method — just copy the URL and paste it in n8n |
| **Download** | If you prefer to save the file locally first |

**Import from URL (recommended):**
1. Copy the URL from the workflow section (starts with `https://raw.githubusercontent.com/...`)
2. In n8n, click **Workflows** → **Add Workflow**
3. Click the **three-dot menu (⋮)** in the top-right
4. Select **Import from URL**
5. Paste the URL and click **Import**
6. Click **Save**

**Import from File:**
1. Click the **Download** link to save the `.json` file
2. In n8n, click **Workflows** → **Add Workflow**
3. Click the **three-dot menu (⋮)** in the top-right
4. Select **Import from File**
5. Choose the downloaded `.json` file
6. Click **Save**

**Run:**
1. Open the workflow in the editor
2. Make sure credentials are set up (Settings → Credentials)
3. Click **Execute Workflow** in the top toolbar
4. Click any node to see its output in the right panel

**Cost safety:** Keep workflows as **Drafts** (don't Publish) while learning. After the first successful AI call, **Pin data** (📌) on that node before editing downstream nodes — this prevents repeated API charges.

---

**Pattern Summary**

| Pattern | When to use | Key nodes |
|---------|-------------|------------|
| **Prompt Chaining** | Complex tasks that benefit from step-by-step refinement | Multiple LLM Chains in sequence |
| **Routing** | Different handling based on input type | LLM (classifier) + Switch |
| **Parallelization** | Independent analyses that can run simultaneously | Multiple branches + Merge |
| **Human-in-the-Loop** | AI output needs human approval before action | LLM + Wait (webhook) |

**Tips for Building Your Own Workflows**

1. **Start simple.** Build one node at a time and test frequently.

2. **Use descriptive node names.** "Step 1: Create Outline" is better than "LLM Chain."

3. **Pin data often.** After any successful LLM call, pin the result before working on the next node.

4. **Check the Output panel.** Switch between Table and JSON views to understand your data.

5. **Use Set nodes as checkpoints.** Save intermediate results with clear field names.

6. **Test routing with different inputs.** Make sure all branches work, not just the happy path.
