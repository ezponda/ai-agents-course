# Multi-Agent Systems

Every agent you've built so far has been a **single agent** — one AI Agent node, one system message, one set of tools. That covers most real tasks. But some jobs are big enough that one agent, juggling everything at once, starts to make worse decisions.

This chapter introduces the **orchestrator-workers** pattern: one *orchestrator* agent that breaks a task into pieces, hands each piece to a focused *worker* agent, and combines the results.

This is the last conceptual pattern in the course — and it completes the set. Prompt Chaining, Routing, Parallelization, Reflection, and now orchestrator-workers are all adapted from Anthropic's [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents).

```{note}
Multi-agent is the most advanced pattern in the course — and the easiest to overuse. By the end of this chapter you'll know how to build it **and**, just as important, when *not* to.
```

---

## The Single-Agent Ceiling

In the First AI Agent and Tool Calling chapters, you gave one agent a handful of tools and it chose between them. That works well — up to a point.

As you pile more tools and responsibilities onto a single agent, two things happen:

- **It picks the wrong tool more often.** Every tool description competes for the model's attention. With 3 tools the choice is easy; with 15 the agent starts guessing.
- **Its instructions get crowded.** A system message that tries to be a researcher, a writer, an editor, and a translator at once does each job worse than four focused prompts would.

You already met this warning in the Tool Calling chapter ("in production systems with 10+ tools, new challenges appear"). Multi-agent is one of the solutions named there — **Router → Specialists**: split the work across focused agents instead of overloading one.

The rule of thumb is qualitative, not a magic number: **keep each agent's job small enough that you could describe it in one sentence.** When you can't, you've hit the ceiling — and that's the signal to split.

---

## What "Multi-Agent" Really Means

The term is overused. Wiring one agent to a search tool and calling it "multi-agent" is not it.

A real multi-agent system has:
- **Distinct agents** — each with its own system message and its own tools
- **A coordination layer** — something that decides which agent runs, when, and with what input

In Anthropic's terms, this is the **orchestrator-workers** pattern: *"a central LLM dynamically breaks down tasks, delegates them to worker LLMs, and synthesizes their results."*

### How it differs from Routing

It's easy to confuse this with the Routing pattern. The difference is **who decides the subtasks**:

| | Routing | Orchestrator-Workers |
|--|---------|----------------------|
| **Branches** | Fixed, defined by you | Decided by the orchestrator at runtime |
| **Decision** | "Which one path?" | "Which agents, in what order, how many times?" |
| **Result** | One branch handles it | The orchestrator combines several agents' work |

Routing picks *one* predefined lane. The orchestrator composes a *plan*. And the key idea that makes it work in n8n: **a sub-agent is just an agent used as a tool** — the orchestrator "calls" the Research Agent the same way an agent calls Calculator or Wikipedia.

---

## How n8n Builds Multi-Agent Systems

There are two ways to connect agents in n8n.

| Approach | What it is | Best for |
|----------|-----------|----------|
| **AI Agent Tool node** | Attach an agent to another agent *as a tool*, on the same canvas | Most cases — this is what we'll use |
| **Execute Workflow (sub-workflow)** | Call a separate workflow that contains an agent | Reusing one agent across many different workflows |

The **AI Agent Tool** node is the newer, simpler approach: the orchestrator sees each worker agent as just another tool it can call — exactly like Calculator or Wikipedia. Everything runs on one canvas, in one execution, so you can watch the whole chain in the output panel. You can even nest them: a worker can have its own workers, for multiple tiers.

```{note}
**This is orchestrated, not autonomous.** n8n runs the *flow* you design — the orchestrator directs which agents run. It does not invent new agents on the fly or keep long-term state between separate runs on its own. If you need agents to share memory across runs, you build that yourself with a database (the same idea as moving RAG to a persistent vector store). For this course that's a feature, not a limitation: the flow is predictable and auditable, every step visible in the execution history.
```

---

## The Workflow: A Content Pipeline

**What you will build:** You give the orchestrator a topic. It calls a **Research Agent** (which looks up facts on Wikipedia), passes the findings to a **Writer Agent**, and returns a short, fact-based article — all from a single run.

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  Manual Trigger │────▶│  Input — Topic  │────▶│  Orchestrator Agent  │────▶│ Output — Article│
└─────────────────┘     └─────────────────┘     └──────────────────────┘     └─────────────────┘
                                                          ┊ (sub-nodes)
                                          ┌───────────────┼─────────────────┐
                                          ┊               ┊                 ┊
                                   ┌────────────┐  ┌──────────────┐  ┌──────────────┐
                                   │ Chat Model │  │ Research     │  │ Writer       │
                                   │  (shared)  │  │ Agent (tool) │  │ Agent (tool) │
                                   └─────┬──────┘  └──────┬───────┘  └──────────────┘
                                         ┊                ┊
                                  (feeds all 3)     ┌──────────┐
                                                    │Wikipedia │
                                                    └──────────┘
```

**New node:** **AI Agent Tool** — an AI Agent attached to another agent as a tool. The workers connect to the orchestrator with the same dotted line used for any tool. All three agents **share one Chat Model** here (one credential to set, less clutter) — but each *could* have its own; in production you might give the workers a cheaper model than the orchestrator.

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/15_multi_agent_content_pipeline.json
> ```
>
> **Download:** {download}`15_multi_agent_content_pipeline.json <_static/workflows/15_multi_agent_content_pipeline.json>`

```{note}
**Cost note.** A multi-agent run makes several LLM calls (the orchestrator plus each worker). It costs more than a single agent — that trade-off is the whole point of **When *Not* to Use Multi-Agent** below. The Research Agent uses **Wikipedia** (free) on purpose, so the only cost here is LLM tokens. Pin data while you build.
```

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow

1. Click **Workflows** → **Add Workflow**
2. Rename it to "Multi-Agent Content Pipeline"

### Step 2: Add the trigger and input

1. Add **Manual Trigger**
2. Add **Edit Fields** → rename to `Input — Topic`
3. Add one String field:

| Name | Value (Expression) |
|------|--------------------|
| `topic` | `{{ $json.topic || "the history of the Eiffel Tower" }}` |

### Step 3: Add the Orchestrator (AI Agent) + the shared Chat Model

1. Add **AI Agent** → rename to `Orchestrator Agent`
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression): `{{ $json.topic }}`
   - **System Message** (in Options):
     ```
     You are the orchestrator of a small content team. Your job is to produce a short, accurate article on the topic the user gives you.

You have two specialist agents available as tools:
- Research Agent: looks up facts. Send it the topic; it returns key facts.
- Writer Agent: writes the article. Send it the research findings; it returns the finished article.

Process:
1. Send the topic to the Research Agent and wait for the facts.
2. Send those facts to the Writer Agent.
3. Return the Writer Agent's article as your final answer — do not rewrite it yourself.

Rules:
- Always research before writing. Never write from your own knowledge.
- Call each specialist once. Do not loop.
- Output ONLY the final article.
     ```
3. Add a **Chat Model** sub-node → **OpenRouter Chat Model** → model `openai/gpt-4o-mini`. **We'll reuse this one model for all three agents** — one credential, less clutter.

### Step 4: Add the Research Agent (AI Agent Tool)

1. Click **+ Tool** at the bottom of the Orchestrator → search for **AI Agent Tool** → add it
2. Rename it to `Research Agent`
3. Configure:
   - **Description** (this is what the orchestrator reads to decide when to call it):
     ```
     Looks up factual information about a topic on Wikipedia. Send it a topic or subject; it returns key facts as bullet points. Use this before writing anything.
     ```
   - **Prompt (User Message)** (Expression): `{{ $fromAI('topic', 'The topic to research', 'string') }}`
   - **System Message** (in Options):
     ```
     You are a research assistant. Given a topic, look it up on Wikipedia and return the key facts.

Rules:
- Use the Wikipedia tool. Do NOT answer from memory.
- Return 4-6 short factual bullet points: dates, names, numbers, what it is.
- No opinions, no introduction, no conclusion. Just the facts.
     ```
4. Give the Research Agent its sub-nodes:
   - **Chat Model** → drag from the **existing OpenRouter Chat Model** to this agent's **Model** input (reuse it — no new node)
   - **Tool** → **Wikipedia** (no credentials needed)

### Step 5: Add the Writer Agent (AI Agent Tool)

1. Click **+ Tool** on the Orchestrator again → add another **AI Agent Tool** → rename to `Writer Agent`
2. Configure:
   - **Description**:
     ```
     Writes a short article from a set of research facts. Send it the facts gathered by the Research Agent; it returns the finished article. Use this after research is done.
     ```
   - **Prompt (User Message)** (Expression): `{{ $fromAI('facts', 'The research facts to write the article from', 'string') }}`
   - **System Message** (in Options):
     ```
     You are a writer. Given a set of research facts, write a short, engaging article.

Rules:
- Use ONLY the facts provided. Do not add information from your own knowledge.
- 2-3 short paragraphs, plain language, no headings.
- Start with the most interesting fact, not a generic introduction.
- Output ONLY the article.
     ```
3. Connect the **same OpenRouter Chat Model** to the Writer's **Model** input. The Writer needs no tools.

```{tip}
**Shared vs. own model.** One Chat Model feeding all three agents is the simplest setup. You can also give an agent its **own** model — for example a cheaper, faster model for the workers and a stronger one for the orchestrator. The agents stay distinct either way: each has its own system message and tools.
```

```{important}
**Do not connect Memory to the worker agents.** Keep workers stateless — see **What to Watch Out For**. The orchestrator passes everything a worker needs in the prompt.
```

### Step 6: Add the Output

1. Add **Edit Fields** → rename to `Output — Article`
2. Add one String field:
   - `article` (Expression): `{{ $json.output }}`
3. Enable **Keep Only Set**

### Step 7: Connect and test

```
Manual Trigger → Input — Topic → Orchestrator Agent → Output — Article
```

1. Click **Execute Workflow**
2. Click the **Orchestrator Agent** and expand the execution details — you'll see it call **Research Agent**, then **Writer Agent**, in order.

::::

### Meet the Node: AI Agent Tool

This pattern introduces one new node: the **AI Agent Tool**.

| Property | Description |
|----------|-------------|
| **What it is** | A full AI Agent that another agent can call as a tool |
| **Description** | The text the orchestrator reads to decide *when* to call this worker — write it like any tool description ("Use this when…") |
| **Prompt (User Message)** | What the worker receives. Use `{{ $fromAI('…') }}` so the orchestrator fills it in at runtime |
| **System Message** | The worker's own instructions and role |
| **Sub-nodes** | Each worker needs a **Chat Model** (they can share one, as we do here, or each use its own) and can have its own Tools and (optionally) Memory |
| **Connection** | Connects to the orchestrator with a **dotted line**, like any tool |

**The key idea:** to the orchestrator, the Research Agent is just a tool named `Research Agent` with a description. The orchestrator doesn't know or care that there's a whole agent behind it. This is why the `Description` field matters as much as it did for the HTTP Request Tool — it's the only thing the orchestrator sees.

**See the Tool Calling chapter** for how tool descriptions drive the agent's choice, and the **Node Toolbox** appendix for the AI Agent node itself.

### Node-by-Node Walkthrough

| Node | Type | What it does |
|------|------|-------------|
| **Manual Trigger** | Trigger | Starts the workflow |
| **Input — Topic** | Set | Creates the `topic` field (with a default for testing) |
| **Orchestrator Agent** | AI Agent | Reads the topic, calls the two worker agents in order, returns the final article → `output` |
| **Output — Article** | Set | Saves `{{ $json.output }}` as `article` |

**Sub-nodes (dotted lines):**

| Sub-node | Type | Purpose |
|----------|------|---------|
| **OpenRouter Chat Model** | Chat Model | The shared brain — feeds the orchestrator *and* both workers |
| **Research Agent** | AI Agent Tool | Worker: looks up facts on Wikipedia |
| **Writer Agent** | AI Agent Tool | Worker: writes the article from the facts |
| **Wikipedia** | Tool | Connected to the Research Agent (not the orchestrator) |

One Chat Model feeds all three agents here — fewer nodes, one credential to set. They are still **separate agents**: each has its own system message (and its own tools). If you wanted, you could give a worker its own model — e.g. a cheaper one — without changing anything else.

### System Messages

Each agent has a focused role. This is the whole point — three small, clear prompts instead of one overloaded one.

**Orchestrator Agent:**
```
You are the orchestrator of a small content team. Your job is to produce a short, accurate article on the topic the user gives you.

You have two specialist agents available as tools:
- Research Agent: looks up facts. Send it the topic; it returns key facts.
- Writer Agent: writes the article. Send it the research findings; it returns the finished article.

Process:
1. Send the topic to the Research Agent and wait for the facts.
2. Send those facts to the Writer Agent.
3. Return the Writer Agent's article as your final answer — do not rewrite it yourself.

Rules:
- Always research before writing. Never write from your own knowledge.
- Call each specialist once. Do not loop.
- Output ONLY the final article.
```

**Research Agent** (Description the orchestrator sees: *"Looks up factual information about a topic on Wikipedia. Send it a topic or subject; it returns key facts as bullet points. Use this before writing anything."*):
```
You are a research assistant. Given a topic, look it up on Wikipedia and return the key facts.

Rules:
- Use the Wikipedia tool. Do NOT answer from memory.
- Return 4-6 short factual bullet points: dates, names, numbers, what it is.
- No opinions, no introduction, no conclusion. Just the facts.
```

**Writer Agent** (Description the orchestrator sees: *"Writes a short article from a set of research facts. Send it the facts gathered by the Research Agent; it returns the finished article. Use this after research is done."*):
```
You are a writer. Given a set of research facts, write a short, engaging article.

Rules:
- Use ONLY the facts provided. Do not add information from your own knowledge.
- 2-3 short paragraphs, plain language, no headings.
- Start with the most interesting fact, not a generic introduction.
- Output ONLY the article.
```

**Why this works:** the orchestrator's prompt never explains *how* to research or *how* to write — it only knows it has two specialists and the order to call them. Each worker owns its own craft. Compare this to cramming "research on Wikipedia, then write a 3-paragraph article using only those facts" into a single agent: the workers keep each instruction set short enough to follow reliably.

### Data Flow

```
INPUT                          OUTPUT
─────                          ──────
Trigger: { }
    ↓
Input — Topic: { topic: "the history of the Eiffel Tower" }
    ↓
Orchestrator Agent:
  1. Calls Research Agent("the history of the Eiffel Tower")
        → "- Built 1887-1889 for the 1889 World's Fair
           - Designed by Gustave Eiffel's company
           - 330 m tall; was the tallest structure until 1930 ..."
  2. Calls Writer Agent(those facts)
        → "When the Eiffel Tower opened in 1889, it was the tallest ..."
  3. Returns the article
    ↓
Output — Article: { article: "When the Eiffel Tower opened in 1889 ..." }
```

::::{dropdown} 🔍 How the orchestrator calls a worker. See the tool call
:color: info

To the orchestrator, calling the Research Agent looks exactly like calling any tool. The worker's `Description` is what the orchestrator reads; the `$fromAI()` prompt is what the orchestrator fills in.

```
                    ┌─────────────────────────────────────────────┐
                    │           ORCHESTRATOR (Loop 1)             │
                    │  "I have a topic. My rules say research      │
                    │   first. I'll call the Research Agent tool." │
                    └─────────────────────────────────────────────┘
                                        │
                                        ▼  calls tool "Research Agent"
                    ┌─────────────────────────────────────────────┐
                    │            RESEARCH AGENT (a worker)        │
                    │  Receives: "the history of the Eiffel Tower" │
                    │  Calls its OWN Wikipedia tool → reads facts  │
                    │  Returns: "- Built 1887-1889 ..."            │
                    └─────────────────────────────────────────────┘
                                        │
                                        ▼  back to orchestrator
                    ┌─────────────────────────────────────────────┐
                    │           ORCHESTRATOR (Loop 2)             │
                    │  "I have facts. Now I'll call the Writer."   │
                    └─────────────────────────────────────────────┘
                                        │
                                        ▼  calls tool "Writer Agent"
                    ┌─────────────────────────────────────────────┐
                    │             WRITER AGENT (a worker)         │
                    │  Receives: the facts                         │
                    │  Returns: the finished article               │
                    └─────────────────────────────────────────────┘
                                        │
                                        ▼
                    ┌─────────────────────────────────────────────┐
                    │  ORCHESTRATOR: returns the article as output │
                    └─────────────────────────────────────────────┘
```

**Key insight:** each worker runs its own loop (the Research Agent even has its own Think → Wikipedia → answer cycle). The orchestrator only sees the *result* a worker returns, not its internal steps.

::::

---

## When *Not* to Use Multi-Agent

This is the most important section in the chapter. Multi-agent is powerful and expensive, and most production workflows do **not** need it.

**The default is one well-scoped agent with a human in the loop.** Reach for multi-agent only when a single agent has genuinely hit the ceiling from earlier — too many tools, or instructions pulling in too many directions — and usually it hasn't.

### The cost is real

In Anthropic's [research on multi-agent systems](https://www.anthropic.com/engineering/built-multi-agent-research-system), a multi-agent setup (a lead agent with worker subagents) outperformed a single agent by **90.2%** on their internal research evaluation. That's the headline people quote. Here's the part they leave out:

> "Agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens as chats."

Anthropic also found that, on one browsing benchmark, **token usage alone explained ~80% of the score differences** — a large part of the gain came simply from spending far more tokens. For a course where you pay per token, that 15× matters more than the 90%.

### When it fits — and when it doesn't

| Good fit | Poor fit |
|----------|----------|
| Independent subtasks (research several things at once) | Tasks where every agent needs the same shared context |
| A clear division of labor (research vs. write) | Tightly coupled steps with many dependencies |
| The quality gain is worth paying 5-15× the tokens | Anything a single agent already does well enough |

Anthropic's own guidance: *"some domains that require all agents to share the same context or involve many dependencies between agents are not a good fit for multi-agent systems today."* Their example — most coding tasks have fewer truly parallel pieces than research does.

**Honest takeaway:** if a single agent with good tools and a human approval gate already does the job, that is the better system. Multi-agent buys quality at a steep, ongoing cost.

---

## What to Watch Out For

| Topic | What to know |
|-------|-------------|
| **Keep workers stateless** | Don't connect Memory to worker agents. A worker should do its job from the prompt it's handed and forget it. If two unrelated runs share a worker's memory, context bleeds between them and you get subtle, hard-to-debug wrong answers. Memory belongs on the orchestrator (or the Chat Trigger), not the workers. |
| **Cost multiplies** | Every worker call is a full agent run. Three agents calling each other can easily be 5-15× the tokens of one agent. Pin data while building; set **Max Iterations** on every agent. |
| **Watch the loops** | Each agent has its own loop *and* the orchestrator loops over the workers. Tell the orchestrator to "call each specialist once. Do not loop." A confused orchestrator that re-calls a worker repeatedly burns tokens fast. |
| **Descriptions are everything** | The orchestrator chooses workers purely from their `Description`. Vague descriptions cause wrong or skipped calls — the same rule as tool descriptions in the Tool Calling chapter. |
| **It's still a draft until tested** | Multi-agent flows have the most moving parts of anything in the course. Run it, expand the execution details, and confirm the call order before you rely on it. |

### Where this connects

- **Routing** picks one predefined branch; the orchestrator dynamically composes a plan across agents. A sub-agent is just an agent used as a tool.
- **Reflection** inside a single agent becomes a separate **Editor Agent** here — a worker whose only job is to critique and improve the Writer's draft. That's the optional challenge below.

---

## Try It Yourself

1. **Change the topic.** Edit `Input — Topic` (or run from a Chat Trigger) and try "the rules of chess" or "how vaccines work". Watch the call order in the execution details.

2. **Challenge — add an Editor Agent (Reflection across agents).** Add a third AI Agent Tool called `Editor Agent` whose job is to check the Writer's draft against the facts and tighten it. Update the orchestrator's process to: Research → Write → Edit → return. This is the Reflection pattern, but split across agents instead of looping inside one.
   - **Done when:** the orchestrator calls all three workers in order and the final article is visibly cleaner than the Writer's first draft.

3. **Challenge — break it on purpose.** Give the Writer Agent a Window Buffer Memory with a fixed session key, run two different topics, and watch the second article get "contaminated" by the first. Then remove the memory. This shows *why* workers stay stateless.

4. **Stretch — make it a chat app.** Swap the Manual Trigger for a Chat Trigger and rename the output field to `output`. You now have a conversational research-and-write assistant — and a perfect candidate for the next project, where you connect it to your own front end.

---

## Summary

| Concept | Key Point |
|---------|-----------|
| **Single-agent ceiling** | One agent gets worse as you pile on tools and responsibilities |
| **Orchestrator-workers** | A central agent breaks down the task, delegates to focused workers, and combines results |
| **vs. Routing** | Routing picks one fixed branch; the orchestrator composes a plan at runtime |
| **AI Agent Tool node** | Attach an agent to another agent as a tool — one canvas, one execution |
| **Each worker is its own agent** | Own system message and tools; the Chat Model can be shared or per-agent |
| **Keep workers stateless** | No memory on workers — avoids cross-run contamination |
| **Cost** | Multi-agent uses ~15× the tokens of a single chat (Anthropic) — use it only when a single agent has truly hit its ceiling |

**Key insight:** multi-agent isn't a smarter kind of AI — it's the same agents you already know, organized into a team. The skill is knowing when the team is worth the cost. Most of the time, one good agent wins.

**Docs:** [AI Agent Tool node](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolaiagent/) · [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)

This is the last conceptual chapter. Next come the **Projects**, where you combine everything — including, in Project 6, connecting an agent to your own app.
