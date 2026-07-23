# Core Concepts: Data Flow and Expressions

In the Quick Start chapter, you built a working workflow and learned the basics hands-on. This chapter deepens your understanding so you can build more complex workflows.

**What's covered:**
- How data flows between nodes
- Connection types (solid vs dotted lines)
- Expressions in more detail
- Draft, Test mode, and Publishing to production

---

## How Data Flows

In Quick Start, you saw data move from Edit Fields to Basic LLM Chain. Here's a deeper look at how this works.

### Items

n8n passes data as a **list of items**. Each item is a JSON object:

```json
[
  { "topic": "coffee", "style": "funny" },
  { "topic": "rain", "style": "sad" }
]
```

When a node receives 2 items, it processes each one and outputs 2 results.

### Input and Output

Every node has:
- **Input** — what it receives from the previous node
- **Output** — what it sends to the next node

```
[Node A] ──output──▶ [Node B] ──output──▶ [Node C]
              (input)             (input)
```

Click any node after running to see both tabs in the Output Panel.

---

## Connection Types

You've seen two types of lines connecting nodes:

| Line Type | What it means | Example |
|-----------|---------------|--------|
| **Solid line** | Data flows from one node to the next | Edit Fields → LLM Chain |
| **Dotted line** | Capability connection (no data flows) | Chat Model → LLM Chain |

### Solid Lines = Data Flow

When you connect nodes with a solid line, the output of the left node becomes the input of the right node. Data always flows **left-to-right**.

### Dotted Lines = Capabilities

Dotted lines connect **sub-nodes** that provide capabilities:
- **Chat Model** → provides AI capability to LLM Chain
- **Memory** → provides conversation history to AI Agent
- **Tools** → provide actions to AI Agent

No data flows through dotted lines. They just say "this node can use that capability."

---

## Triggers

Every workflow starts with a **Trigger** — the leftmost node that defines what starts the workflow.

| Trigger | When it fires |
|---------|---------------|
| **Manual Trigger** | You click "Execute Workflow" |
| **Schedule Trigger** | On a timer (hourly, daily, etc.) |
| **Webhook Trigger** | When another service sends a request |
| **Chat Trigger** | When a user sends a chat message |

**In this course:** We use Manual Trigger for most examples. Chat Trigger appears in the AI Agent chapter for conversations.

---

## Workflow Lifecycle: Test, Draft, Published

Since n8n 2.4 (Jan 2026) every workflow has three states you'll encounter:

| State | How it runs | When to use |
|-------|-------------|-------------|
| **Test (manual execute)** | You click "Execute Workflow" | While building and debugging |
| **Draft** | Auto-saved every 2 seconds while you edit. Runs only on manual execute. | The default editing state — nothing reaches production yet |
| **Published** | Runs automatically when its trigger fires (webhook, schedule, chat) | Once your workflow is ready for real use |

**Stay in Draft + Test mode while learning.** This gives you control and lets you use pinned data — no surprise API calls.

When you're ready to promote a draft to production, click **Publish** in the top-right of the editor. You can keep editing the draft afterwards — your changes stay isolated until you publish again.

```{note}
**If you've used n8n before 2026:** the old "Save and Activate" / Active toggle paradigm was replaced by Save/Publish + Autosave in n8n 2.4. If you see an "Active" toggle in screenshots online, that's the old UI — the concept is the same but the button is now called *Publish*.
```

---

## The Output Panel (Review)

You used this in Quick Start. Here's a quick reference:

| View | When to use |
|------|-------------|
| **Table** | Quick reading of data |
| **JSON** | Finding exact field names for expressions |
| **Schema** | Understanding data structure |

**Pro tip:** Always check JSON view before writing an expression. Field names are case-sensitive!

---

## Pinning Data (Review)

You learned pinning in Quick Start. Key points:

- **Pin** = save a node's output to reuse without re-running
- **Why:** Saves money (no API calls), saves time, keeps data stable
- **When:** After LLM calls, after slow operations, while debugging
- **How:** Click the pin icon (📌) in the Output Panel

**Remember:** Pinned data only works in Test mode.

---

## Expressions Deep Dive

In Quick Start, you used `{{ $json.topic }}` to pass data. Here's a closer look at expressions.

### The Basics

| Expression | What it does |
|------------|-------------|
| `{{ $json.field }}` | Read a field from the previous node |
| `{{ $json.user.name }}` | Read a nested field |
| `Hello {{ $json.name }}` | Mix text with data |

### Fixed vs Expression Mode

Every input field has two modes:
- **Fixed** — literal text, `{{ }}` is treated as text
- **Expression** — `{{ }}` is evaluated as code

If your expression isn't working, check that you're in Expression mode (click the field to toggle).

### Referencing a Specific Node

Sometimes you need data from a node that isn't directly before the current one. There are two equivalent syntaxes:

```
{{ $node["Edit Fields"].json.topic }}
{{ $('Edit Fields').item.json.topic }}
```

Both work the same way. The `$('Node Name')` syntax is newer and shorter. Use whichever you prefer — just be consistent.

You'll see this pattern in the Routing example, where specialists access the original input directly.

### Common Expressions

Beyond reading fields, n8n has built-in expressions for common tasks.

**Date and Time:**

| Expression | Result |
|------------|--------|
| `{{ $now }}` | Current date and time |
| `{{ $today }}` | Today at midnight |
| `{{ $now.format('yyyy-MM-dd') }}` | Formatted: `2025-01-25` |
| `{{ $now.format('HH:mm') }}` | Formatted: `14:30` |

**Conditionals:**

| Expression | What it does |
|------------|--------------|
| `{{ $if($json.age > 18, "adult", "minor") }}` | If-then-else |
| `{{ $ifEmpty($json.name, "Anonymous") }}` | Default if empty |

**Text Manipulation:**

| Expression | Result |
|------------|--------|
| `{{ $json.name.toUpperCase() }}` | `JOHN` |
| `{{ $json.name.toLowerCase() }}` | `john` |
| `{{ $json.text.replace("old", "new") }}` | Replace text |
| `{{ $json.email.split("@")[0] }}` | Get part before `@` |

**Workflow Info:**

| Expression | What it returns |
|------------|-----------------|
| `{{ $workflow.name }}` | Name of current workflow |
| `{{ $execution.id }}` | Unique ID of this run |
| `{{ $itemIndex }}` | Current item index (0, 1, 2...) |

**Tip:** These work anywhere you can write expressions. Combine them: `{{ $now.format('yyyy-MM-dd') }}: {{ $json.message.toUpperCase() }}`

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Expression shows literally | Switch from Fixed to Expression mode |
| Field not found | Check spelling and case in JSON view |
| Data seems stale | Check if a node is pinned |
| Node has red error | Click it and read the error in Output Panel |

For detailed troubleshooting, see the **Node Toolbox** appendix.

---

## Summary

| Concept | Key Point |
|---------|----------|
| **Items** | Data flows as a list of JSON objects |
| **Solid lines** | Data flow between nodes |
| **Dotted lines** | Capability connections (no data) |
| **Triggers** | What starts the workflow |
| **Draft vs Published** | Edit in Draft (autosaved); click Publish to deploy |
| **Test mode** | Manual runs while building (works for Drafts too) |
| **Expressions** | `{{ $json.field }}` to pass data dynamically |
| **Common expressions** | `$now`, `$if()`, `.toUpperCase()` for dates, logic, text |
| **Pinning** | Save output to avoid re-running |

---

## Next Steps

You now have a solid foundation. Time to see these concepts in action!

Proceed to the **Workflow Examples** chapter to learn four workflow patterns:
1. **Prompt Chaining** — break complex tasks into steps
2. **Routing** — send data down different paths
3. **Parallelization** — run analyses simultaneously
4. **Human-in-the-Loop** — require approval before taking action

Each pattern builds on what you know. The **Node Toolbox** appendix is your reference for detailed node documentation.
