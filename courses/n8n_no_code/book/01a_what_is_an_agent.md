# What is an AI Agent?

Before building workflows, let's understand the key difference between a **simple LLM call**, a **workflow**, and an **agent**.

This will help you choose the right approach for each task.

---

## The Problem with Single LLM Calls

A simple LLM call works like this:

```
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│   Your prompt   │────────▶│       LLM       │────────▶│  Text response  │
└─────────────────┘          └─────────────────┘          └─────────────────┘
```

**Great for:** Translation, summaries, rewriting — simple one-step tasks.

**Limitations:**
- Only produces text (can't check facts, can't take real actions)
- One attempt — if it's wrong, you have to catch the error yourself
- Complex prompts often lead to errors and invented details

---

## Solution 1: Workflows (You Control the Steps)

Instead of one complex prompt, break the task into smaller steps:

```
                            👤 YOU design this sequence
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│    STEP 1     │──────────▶│    STEP 2     │──────────▶│    STEP 3     │
│  Extract info │           │  Improve it   │           │  Write draft  │
└───────────────┘           └───────────────┘           └───────────────┘
```

**Key characteristics:**
- **You** decide the steps in advance
- Fixed sequence — always runs the same way
- Each step is simpler → fewer errors
- Tools are optional, but **you** choose them at design time (not the AI)

**In n8n:** You connect nodes like Basic LLM Chain, Switch, and Merge — you control the sequence.

---

## Solution 2: Agents (AI Controls the Steps)

An agent is different — **the AI decides what to do next**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              🤖 AGENT LOOP                                  │
│                                                                             │
│    ┌──────────────────────────────────────────────────────────────────┐    │
│    │                                                                  │    │
│    │    ┌─────────┐      ┌─────────┐      ┌─────────┐                │    │
│    │    │  THINK  │─────▶│   ACT   │─────▶│  CHECK  │                │    │
│    │    │         │      │         │      │         │                │    │
│    │    │ "What   │      │  Call   │      │ "Do I   │                │    │
│    │    │  do I   │      │  tool   │      │  have   │───── No ───────┤    │
│    │    │  need?" │      │         │      │ enough?"│                │    │
│    │    └─────────┘      └────┬────┘      └────┬────┘                │    │
│    │                          │                │                     │    │
│    │                          ▼                │ Yes                 │    │
│    │                    ┌──────────┐           │                     │    │
│    │                    │  TOOLS   │           ▼                     │    │
│    │                    │──────────│    ┌─────────────┐              │    │
│    │                    │Calculator│    │FINAL ANSWER │              │    │
│    │                    │Wikipedia │    └─────────────┘              │    │
│    │                    │  Email   │                                 │    │
│    │                    └──────────┘                                 │    │
│    │                                                                  │    │
│    └──────────────────────────────────────────────────────────────────┘    │
│                                 ▲                                          │
│                                 │                                          │
│                          Repeat if needed                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key characteristics:**
- **AI** decides the next step
- Can use **tools** (Calculator, Wikipedia, APIs, databases...)
- **Loops** until the task is complete
- Can **adapt** when something doesn't work

**In n8n:** This is the AI Agent node — you give it tools, and it decides when to use them.

---

## The Key Question: Who Decides?

| Approach | Who decides the steps? | Who decides tools? | Loops? | Best for |
|----------|------------------------|-------------------|--------|----------|
| **Simple LLM** | You (one prompt) | No tools | No | Quick text tasks |
| **Workflow** | You (predefined steps) | You (at design time) | No | Predictable, structured tasks |
| **Agent** | AI (dynamic) | AI (at runtime) | Yes | Complex, ambiguous tasks |

**Rule of thumb:**
- If you can write down all the steps → use a **workflow**
- If the AI needs to figure it out → use an **agent**

---

## Agent Building Blocks

Every AI agent is built from four core components:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AI AGENT                                       │
│                                                                             │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   │
│   │     LLM     │   │    TOOLS    │   │   MEMORY    │   │  REASONING  │   │
│   │   (brain)   │   │  (actions)  │   │  (context)  │   │   (logic)   │   │
│   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   │
│                                                                             │
│   Understands       Interacts with     Remembers          Decides what      │
│   language          the real world     conversations      to do next        │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Component | What it does | Examples in n8n |
|-----------|--------------|-----------------|
| **LLM** | Reasoning, language understanding | OpenRouter, OpenAI, Google AI |
| **Tools** | Actions the agent can take | Calculator, Wikipedia, HTTP Request |
| **Memory** | Conversation history | Window Buffer Memory (short-term), Vector Store (long-term) |
| **Reasoning** | Planning, deciding next steps | ReAct loop (built into AI Agent node) |

### Agentic Design Patterns

The AI community identifies four main patterns for building agents:

| Pattern | What it means |
|---------|---------------|
| **Tool Use** | Agent calls external tools to take actions |
| **Reflection** | Agent reviews and improves its own output |
| **Planning** | Agent breaks complex tasks into steps before acting |
| **Multi-agent** | Multiple agents collaborate on a task |

**Tool Use** is the most practical starting point — once you understand how agents call tools, the other patterns build naturally on top.

```{note}
For a deeper dive into agent design, see [Anthropic's Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents).
```

---

## What Agents Struggle With

Agents are powerful, but they have real limitations. Understanding these helps you design better systems:

| Limitation | Why it happens | How to handle it |
|------------|----------------|------------------|
| **Counting and math** | LLMs predict text, not compute | Use Calculator tool |
| **Current information** | Training data has a cutoff date | Use Search/Wikipedia tools |
| **Long-term memory** | Context window is limited | Use Memory nodes for conversations |
| **Complex multi-step plans** | Hard to keep track of many steps | Break into smaller workflows |
| **Following instructions exactly** | May ignore constraints | Add validation, use Reflection pattern |

**Key insight:** Tools exist because LLMs have gaps. A Calculator tool isn't a luxury — it's necessary because LLMs genuinely struggle with arithmetic. Design your agents knowing these limitations.

---

## What You'll Build in This Course

| Chapter | What you build | Approach |
|---------|----------------|----------|
| Quick Start | Topic explainer | Simple LLM call |
| Workflow Examples | Prompt chaining, routing, parallelization, human-in-the-loop | Workflows (you control) |
| Reflection Pattern | Constrained writing with self-improvement | From workflow to agent |
| First AI Agent | Calculator, SerpAPI, Chat with memory | Agents (AI controls) |

By the end, you'll know when to use each approach — and how to build them in n8n.

**Let's start building!** Proceed to **Setup** to install n8n.
