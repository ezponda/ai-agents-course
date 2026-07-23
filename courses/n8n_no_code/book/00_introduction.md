# Agentic AI with n8n

Build AI systems that think, decide, and act — without writing code.

This course teaches you to create **AI agents** using n8n, a visual workflow tool. By the end, you'll understand when to use a simple prompt, when to build a workflow, and when to deploy a full agent.

---

## Why AI Agents?

**The problem:** Large Language Models (like GPT) are powerful, but limited:
- They only produce text — they can't check facts or take real actions
- One attempt — if they're wrong, you catch the error
- Complex prompts often lead to errors and invented details

**The solution:** AI Agents go beyond simple prompts:
- They **use tools** (calculator, search, APIs) to get real information
- They **loop** until the task is complete
- They **decide** the next step based on results

**Why n8n:** Visual, drag-and-drop interface. Perfect if you're not a programmer. You see exactly what's happening at each step.

---

## What You'll Build

The course introduces **four workflow patterns** — the building blocks for everything that comes next:

```
PATTERN 1: Prompt Chaining                    PATTERN 2: Smart Routing
──────────────────────────                    ────────────────────────

  ┌────────┐   ┌────────┐   ┌────────┐          ┌─────────┐    ┌──▶ Refund Agent
  │Outline │──▶│ Edit   │──▶│ Draft  │          │Classify │────┼──▶ Order Agent
  └────────┘   └────────┘   └────────┘          │ Ticket  │    └──▶ Support Agent
                                                └─────────┘
  You control the steps                         AI routes to the right handler


PATTERN 3: Parallelization                    PATTERN 4: Human-in-the-Loop
──────────────────────────                    ────────────────────────────

      ┌─▶ Facts     ─┐                          ┌────────┐    ┌────────┐
Input ├─▶ Sentiment ─┼─▶ Merge                  │ Draft  │───▶│ ⏸ Wait │──▶ Send
      └─▶ Draft     ─┘                          └────────┘    └────────┘
                                                         Human approves
  Independent analyses combined                 AI drafts, human approves
```

These patterns are your foundation. Once you master them, you'll have the building blocks to create more sophisticated systems on your own.

All without writing a single line of code.

```{note}
These patterns are adapted from Anthropic's [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — recommended reading after completing the course.
```

---

## Course Structure

The course has three parts: **Course** teaches the concepts, **Projects** apply them in complete examples, and **Appendices** are references you come back to.

### Course

| Chapter | What you'll do |
|---------|----------------|
| **What is an AI Agent?** | Understand the difference between workflows and agents |
| **Setup** | Install n8n on your computer |
| **Quick Start** | Build your first AI workflow from scratch |
| **Core Concepts** | Understand data flow, expressions, and debugging |
| **Workflow Examples** | Learn four patterns: chaining, routing, parallelization, human-in-the-loop |
| **Reflection Pattern** | Build self-improving loops (manual vs agent) |
| **First AI Agent** | Build agents with tools and memory |
| **Tool Calling** | How agents use tools safely |
| **Guardrails & Safety** | Protect agents from prompt injection and validate outputs |
| **RAG** | Teach your AI to search and use your own documents |
| **Multi-Agent Systems** | Orchestrate specialist agents — and learn when one agent is enough |
| **Where n8n Fits** | When to use n8n — and when to reach for a coding agent |

### Projects

End-to-end builds that combine techniques from multiple chapters. Each project is self-contained — pick whichever interests you.

| Project | What you'll build |
|---------|-------------------|
| **Project 1: Recipe Assistant** | A chat agent that searches real APIs, remembers your conversation, and generates shopping lists |
| **Project 2: Ask Your Data** | Ask natural-language questions about a Spotify dataset — the agent writes and runs JavaScript code to answer them |
| **Project 3: AI Expense Assistant** | A **vision** agent: drop a photo of a receipt in the chat and it reads it, checks it is readable, not a duplicate and within policy, then logs it — talking you through anything wrong |
| **Project 4: Daily Digest** | A **proactive** agent on a schedule: every morning it pulls the day's top tech stories, writes a short briefing and saves it — no chat, it runs on its own |
| **Project 5: Deploy to Production** | Take a workflow from your laptop to a public server using Railway or n8n Cloud |
| **Project 6: Connect Your App** | Call your n8n agent from your own Lovable/Replit front end via a webhook |
| **Project 7: Salon Booking Assistant** | A multi-agent WhatsApp-style receptionist for a hair salon — it books, cancels and answers questions, and politely declines everything else |

### Appendices

Reference material to consult as needed — not meant to be read cover-to-cover.

| Appendix | What it covers |
|----------|----------------|
| **A: Node Toolbox** | Every core node: parameters, output fields, common mistakes |
| **B: Going Live** | Schedule triggers, webhooks, error handling, production checklist, deployment |
| **C: Specialized AI Nodes** | Text Classifier, Sentiment Analysis, Information Extractor, and more |
| **D: Prompt Engineering Basics** | 6 techniques to write better prompts |
| **E: Prompt Engineering for Agents** | ReAct loop, tool descriptions, system prompt templates |
| **F: Selected Resources** | Papers, courses, and guides for going deeper |

---

## Prerequisites

- **n8n**: Install with `npm install -g n8n` and launch with `n8n` — see the **Setup** chapter for full instructions (Mac/Windows)
- **API key**: From [OpenRouter](https://openrouter.ai/), [OpenAI](https://platform.openai.com/), or [Google AI](https://aistudio.google.com/)

**About costs:** Some workflows call paid AI APIs. Run in **Test mode** while learning and leave them as **Drafts** (unpublished) until you're ready — drafts only run when you click *Execute*, never on their trigger. Tools like Wikipedia and Calculator are free.

---

## Next Steps

Proceed to **What is an AI Agent?** to understand the key concepts, then install n8n in **Setup**.
